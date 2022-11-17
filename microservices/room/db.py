from sqlalchemy import create_engine
import json
import os
import logging


class DButil():
    engine = None
    database_uri = None

    def __init__(self, credentials=None):

        if not credentials:
            env = json.loads(os.environ.get('dbsecret', "{}"))
            print(env)
            self.user = env['username']
            self.password = env['password']
            self.host = env['host']
            self.port = env['port']
            self.database = 'postgres'
        else:
            self.user = credentials['username']
            self.password = credentials['password']
            self.host = credentials['host']
            self.port = credentials['port']
            self.database = 'postgres'
        self.logger = logging.getLogger()
        self.connect()

    def connect(self):
        try:
            DButil.database_uri = f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
            DButil.engine = create_engine(
                url=
                f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
            )
            self.logger.critical(
                f"Connection to the {self.host} for user {self.user} created successfully."
            )
        except Exception as ex:
            self.logger.critical(
                "Connection could not be made due to the following error: \n",
                ex)

    # Make sure to dispose the engine when you are done
    def close(self):
        if DButil.engine:
            DButil.engine.dispose()