import unittest
from dataclasses import dataclass
from typing import Dict
from unittest.mock import MagicMock

from atc.etl import Extractor, Loader, Orchestration, MultiInputTransformer
from autofaker import Autodata
from pyspark.sql import DataFrame

from functools import reduce
from pyspark.sql import DataFrame


class TimestampTransformer(MultiInputTransformer):
    def process_many(self, dataset: Dict[str, DataFrame]) -> DataFrame:
        return reduce(DataFrame.unionAll, dataset.values())


class PassLoader(Loader):
    def save(self, df: DataFrame) -> DataFrame:
        return df


class BasicIngestionTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        @dataclass
        class Person:
            id: int
            name: str
            address: str

        extractor: Extractor = MagicMock()
        extractor.read.return_value = Autodata.create_spark_dataframe(Person, use_fake_data=True)

        df = (Orchestration
              .extract_from(extractor)
              .extract_from(extractor)
              .transform_with(TimestampTransformer())
              .load_into(PassLoader())
              .build()
              .execute())

        df.show()

        cls.result = df

    def test_returns_dataframe(self):
        self.assertIsNotNone(self.result)

    def test_returned_dataframe_contains_id_column(self):
        self.assertTrue(self.result.columns.__contains__('id'))

    def test_returned_dataframe_contains_id_column(self):
        self.assertTrue(self.result.columns.__contains__('id'))

    def test_returned_dataframe_contains_name_column(self):
        self.assertTrue(self.result.columns.__contains__('name'))

    def test_returned_dataframe_contains_address_column(self):
        self.assertTrue(self.result.columns.__contains__('address'))
