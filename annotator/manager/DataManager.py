import json
from datetime import datetime
from django.db import IntegrityError

from annotator import offline
from annotator.models import *
from annotator.offline.datasets.dataset_converter import DatasetConverter
import annotator.offline.offline_model as offline
from model_preloader import project_dir

"""
Data:

    
    fetch_unlabeled_data(project_id, num): 获取未标注数据
    commit_labeled_data(labeled_data, project_id): 提交已标注数据
"""

import argparse
import json
import os
from operator import itemgetter

import numpy as np
from sklearn.model_selection import train_test_split


class DataManager:

    @staticmethod
    def _write_unlabeled_data_to_file(objects, filepath):
        with open(filepath, mode='w', encoding='utf8') as fw:
            for o in objects:
                tokens, first_args, second_args = DatasetConverter.split_tokens_and_entities(o.data_content)
                example = {
                    "id": o.unlabeled_id,
                    "tokens": tokens,
                    "entities": [first_args, second_args]
                }
                fw.write(json.dumps(example) + "\n")

    @staticmethod
    def fetch_unlabeled_data(project_id: int, num: int = -1) -> dict:
        """
        获取未标注的数据
        关于数据的详细描述请参阅 models.py 文件

        pipeline:
            1. 点击下一页
            2. 前端将取未标注数据的命令发送给后台，附带项目的 id 号和要取出数据的数量
            3. 后端接收命令，检查数据库中是否有足够的数据
            4. 如果没有符合条件的数据，告知前端取数据失败；否则将满足条件数量的数据返回给前端

        :param project_id: 项目 id
        :param num: 要取出的数据条目数量

        :return:
            {
                "status": True,
                "data":
                    [
                        {
                            "id": 1,
                            # 1993年2月15日，李彤出生在吉林某城市。
                            "text": ['This', 'is', 'a', 'test', 'file.'],
                            "predicted_relation": "人-出生地",
                            "predicted_e1_start": 11,
                            "predicted_e1_end": 13,
                            "predicted_e2_start": 16,
                            "predicted_e2_end": 18,
                        },
                        ...
                    ]
                "code": 200,
                "message": "成功取出 num 条数据",
            }
        """

        try:
            objects = UnlabeledData.objects.filter(project_id=Project.objects.get(pk=project_id))
            objects = objects if num == -1 else objects[:num]

            # import pudb
            # pudb.set_trace()

            DataManager._write_unlabeled_data_to_file(
                objects, os.path.join(project_dir, 'temp', 'predict_data.jsonl'))

            predicted_relations = None

            if len(objects) > 0:
                print('Predicting...')

                predicted_relations, probs = offline.predict_data(
                    test_file=os.path.join(project_dir, 'temp', 'predict_data.jsonl'),
                    batch_size=8
                )

                print('Complete.')

            data = []
            for idx, o in enumerate(objects):
                tokens, first_args, second_args = DatasetConverter.split_tokens_and_entities(o.data_content)
                data.append({
                    "id": o.unlabeled_id,
                    "text": tokens,
                    "predicted_relation": predicted_relations[idx],
                    "predicted_e1_start": first_args[0],
                    "predicted_e1_end": first_args[1],
                    "predicted_e2_start": second_args[0],
                    "predicted_e2_end": second_args[1],
                })

            ret_dict = {
                "status": True,
                "data": data,
                "code": 200,
                "message": "Successfully took out " + str(len(objects)) + " pieces of data.",
            }
            print("Successfully took out " + str(len(objects)) + " pieces of data.")
        except IntegrityError as e:
            ret_dict = {
                "status": False,
                "code": -1,
                "message": str(e),
            }
            print("Failed to take out unlabeled data! " + str(e))

        return ret_dict

    @staticmethod
    def commit_labeled_data(labeled_data: list, project_id: int) -> dict:
        """
        将已标注的数据提交到数据库

        pipeline:
            1. 点击提交按钮
            2. 前端将提交数据命令发送给后台，附带已标注好的数据
            3. 后端接收命令，将标注好的数据插入到数据库中，并将其从未标注数据表中删除
            4. 如果中途出现错误，返回所有数据，并附带错误信息

        :param labeled_data: 已标注的数据
            [
                {
                    "text": ['This', 'is', 'a', 'test', 'file.'],

                    "predicted_relation": "Instrument-Agency(e1,e2)",
                    "predicted_e1": "李彤",
                    "predicted_e2": "吉林",
                    "predicted_e1_start": 11,
                    "predicted_e1_end": 12,
                    "predicted_e2_start": 16,
                    "predicted_e2_end": 17,

                    "labeled_relation": "Instrument-Agency(e1,e2)",
                    "labeled_e1": "李彤",
                    "labeled_e2": "吉林",
                    "labeled_e1_start": 11,
                    "labeled_e1_end": 12,
                    "labeled_e2_start": 16,
                    "labeled_e2_end": 17,

                    "additional_info": "",
                },
                ...
            ]

        :return:
            {
                "status": True,
                "code": 200,
                "message": "已标注数据提交成功"
            }
        """
        try:
            project = Project.objects.get(pk=project_id)
            for meta_data in labeled_data:
                print(meta_data['text'])
                e1_start, e1_end = meta_data["labeled_e1_start"], meta_data["labeled_e1_end"]
                e2_start, e2_end = meta_data["labeled_e2_start"], meta_data["labeled_e2_end"]
                meta_data['text'][e1_start] = '<e1>' + meta_data['text'][e1_start]
                meta_data['text'][e1_end - 1] = meta_data['text'][e1_end - 1] + '</e1>'
                meta_data['text'][e2_start] = '<e2>' + meta_data['text'][e2_start]
                meta_data['text'][e2_end - 1] = meta_data['text'][e2_end - 1] + '</e2>'
                sentence = ' '.join(meta_data['text'])

                data = LabeledData(
                    project_id=Project.objects.get(pk=project_id),

                    labeled_time=datetime.now(),
                    labeled_content=sentence,

                    predicted_relation=meta_data["predicted_relation"],
                    predicted_e1_start=meta_data["predicted_e1_start"],
                    predicted_e1_end=meta_data["predicted_e1_end"],
                    predicted_e2_start=meta_data["predicted_e2_start"],
                    predicted_e2_end=meta_data["predicted_e2_end"],

                    labeled_relation=meta_data["labeled_relation"],
                    labeled_e1_start=meta_data["labeled_e1_start"],
                    labeled_e1_end=meta_data["labeled_e1_end"],
                    labeled_e2_start=meta_data["labeled_e2_start"],
                    labeled_e2_end=meta_data["labeled_e2_end"],

                    additional_info=meta_data["additional_info"]
                )

                data.save()
                UnlabeledData.objects.filter(pk=meta_data["unlabeled_id"]).delete()
                project.sentence_labeled += 1
                project.sentence_unlabeled -= 1
            project.save()
            ret_dict = {
                "status": True,
                "code": 200,
                "message": "Labeled data submitted successfully."
            }
            print("Labeled data submitted successfully.")
        except IntegrityError as e:
            ret_dict = {
                "status": False,
                "code": -1,
                "message": str(e),
            }
            print("Failed to commit labeled data! " + str(e))

        return ret_dict


def test(**kwargs):
    converter = DatasetConverter(file_name=kwargs['file_name'],
                                 input_dir=kwargs['input_dir'], output_dir=kwargs['output_dir'])
    converter.run()
