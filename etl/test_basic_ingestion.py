import unittest
from dataclasses import dataclass

from atc.etl import Extractor, Loader, Orchestrator, Transformer
from atc.spark import Spark
from autofaker import Autodata
from pyspark.sql import DataFrame
from pyspark.sql.functions import current_timestamp


class BasicExtractor(Extractor):
    def read(self) -> DataFrame:
        @dataclass
        class Person:
            id: int
            name: str
            address: str

        return Spark.get().createDataFrame(
            Autodata.create_pandas_dataframe(
                Person,
                use_fake_data=True))


class TimestampTransformer(Transformer):
    def process(self, df: DataFrame) -> DataFrame:
        return df.withColumn("timestamp", current_timestamp())


class ByPassLoader(Loader):
    def save(self, df: DataFrame) -> DataFrame:
        return df


class BasicIngestionTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.result = (Orchestrator()
                      .extract_from(BasicExtractor())
                      .transform_with(TimestampTransformer())
                      .load_into(ByPassLoader())
                      .execute()
                      ["TimestampTransformer"])

    def test_returns_dataframe(self):
        self.assertIsNotNone(self.result)

    def test_returned_dataframe_contains_id_column(self):
        self.assertTrue(self.result.columns.__contains__('id'))

    def test_returned_dataframe_contains_name_column(self):
        self.assertTrue(self.result.columns.__contains__('name'))

    def test_returned_dataframe_contains_address_column(self):
        self.assertTrue(self.result.columns.__contains__('address'))

    def test_returned_dataframe_contains_timestamp_column(self):
        self.assertTrue(self.result.columns.__contains__('timestamp'))
