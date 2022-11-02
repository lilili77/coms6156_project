from sqlalchemy import create_engine
import json
import os
import logging

class DButil():
    engine = None

    def __init__(self):
        self.logger = logging.getLogger()

        env = json.loads(os.environ.get('dbsecret',"{}"))
        self.user = env['username']
        self.password = env['password']
        self.host = env['host']
        self.port = env['port']
        self.database = 'postgres'
        self.connect()
    
    def connect(self):
        try:
            DButil.engine = create_engine(
                url=f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
            )
            self.logger.critical(f"Connection to the {self.host} for user {self.user} created successfully.")
        except Exception as ex:
            self.logger.critical("Connection could not be made due to the following error: \n", ex)
            

    def close(self):
        if DButil.engine:
            DButil.engine.dispose()