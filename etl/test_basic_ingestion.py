import unittest
from dataclasses import dataclass
from unittest.mock import Mock

from atc.etl import Extractor, Loader, Orchestrator, Transformer
from atc.spark import Spark
from autofaker import Autodata
from pyspark.sql import DataFrame
from pyspark.sql.functions import current_timestamp


class TimestampTransformer(Transformer):
    def process(self, df: DataFrame) -> DataFrame:
        return df.withColumn("timestamp", current_timestamp())


class BasicIngestionTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        @dataclass
        class Person:
            id: int
            name: str
            address: str

        extractor = Extractor()
        extractor.read = Mock(
            return_value=(Spark.get().createDataFrame(
                Autodata.create_pandas_dataframe(
                    Person,
                    use_fake_data=True))))

        loader = Loader()
        loader.save = Mock(return_value=None)

        cls.result = (Orchestrator()
                      .extract_from(extractor)
                      .transform_with(TimestampTransformer())
                      .load_into(loader)
                      .execute())["TimestampTransformer"]

    def test_returns_dataframe(self):
        self.assertIsInstance(self.result, DataFrame)

    def test_returned_dataframe_contains_id_column(self):
        self.assertTrue(self.result.columns.__contains__('id'))

    def test_returned_dataframe_contains_name_column(self):
        self.assertTrue(self.result.columns.__contains__('name'))

    def test_returned_dataframe_contains_address_column(self):
        self.assertTrue(self.result.columns.__contains__('address'))

    def test_returned_dataframe_contains_timestamp_column(self):
        self.assertTrue(self.result.columns.__contains__('timestamp'))
