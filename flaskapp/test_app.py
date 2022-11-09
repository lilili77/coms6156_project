from flask import Flask
from flask import jsonify
import unittest
from app import app
import json
from unittest.mock import patch, Mock


class AppTestCase(unittest.TestCase):
    
    # @app.route('/rooms', methods = ['POST'])
    # @app.route('/rooms', methods = ['GET'])
    # @app.route('/rooms/:id', methods = ['GET'])
    # @app.route('/rooms/:id', methods = ['DELETE'])
    # @app.route('/rooms/:id', methods = ['PUT'])


############### CREATE
    #test successful creat new 
    @patch('app.connect_to_db',return_value=Mock())
    def test_insert_with_client(self,connect_to_db):
        tester = app.test_client(self)
        test_new_client = { 
            "name": "test_new_client",
            "host_id": 1,
            "video_id": 1
        }
        test_new_client = json.dumps(test_new_client)
        header={ "Content-Type": "application/json"}
        response = tester.post('/rooms',data=test_new_client,headers = header)
        final_output = json.loads(response.data)
        app.test_id = final_output['data']['id']
        self.assertEqual(response.status_code, 201)
        self.assertEqual(final_output['data']['name'], 'test_new_client')
        
    
    #test missing data creat new 
    @patch('app.connect_to_db',return_value=Mock())
    def test_insert_missing_with_client(self,connect_to_db):
        tester = app.test_client(self)
        test_new_client = { 
            "name": "test_new_client",
            "video_id": 4
        }
        test_new_client = json.dumps(test_new_client)
        header={ "Content-Type": "application/json"}
        response = tester.post('/rooms',data=test_new_client,headers = header)
        final_output = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(final_output['message'], 'missing data')


    #test empty input creat new 
    @patch('app.connect_to_db',return_value=Mock())
    def test_insert_empty_with_client(self,connect_to_db):
        tester = app.test_client(self)
        test_new_client = {}
        test_new_client = json.dumps(test_new_client)
        header={ "Content-Type": "application/json"}
        response = tester.post('/rooms',data=test_new_client,headers = header)
        final_output = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(final_output['message'], 'No input data provided')


############### GET

    #test get all rooms
    @patch('app.connect_to_db',return_value=Mock())
    def test_get_all_with_client(self,connect_to_db):
        tester = app.test_client(self)
        response = tester.get('/rooms')
        self.assertEqual(response.status_code, 200)


    #test get one room    
    @patch('app.connect_to_db',return_value=Mock())
    def test_get_with_client(self,connect_to_db):
        tester = app.test_client(self)
        response = tester.get('/rooms/13')
        self.assertEqual(response.status_code, 200)


    #test get one room with wrong id
    @patch('app.connect_to_db',return_value=Mock())
    def test_get_unmatch_with_client(self,connect_to_db):
        tester = app.test_client(self)
        response = tester.get('/rooms/100')
        self.assertEqual(response.status_code, 404)



############### UPDATE

    #test missing host_id update
    @patch('app.connect_to_db',return_value=Mock())
    def test_update_missing_with_client(self,connect_to_db):
        tester = app.test_client(self)
        test_update_client = { 
            "name": "test_new_client",
        }
        test_update_client = json.dumps(test_update_client)
        header={ "Content-Type": "application/json"}
        response = tester.put('/rooms/10',data=test_update_client,headers = header)
        final_output = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(final_output['message'], 'Action not valid, host_id not found')


    #test miss-match host_id
    @patch('app.connect_to_db',return_value=Mock())
    def test_update_unmatch_with_client(self,connect_to_db):
        tester = app.test_client(self)
        test_update_client = { 
            "name": "test_new_client",
            'host_id':10
        }
        test_update_client = json.dumps(test_update_client)
        header={ "Content-Type": "application/json"}
        response = tester.put('/rooms/10',data=test_update_client,headers = header)
        final_output = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(final_output['message'], 'Action not valid, host_id not match')


    #test non-exist room update
    @patch('app.connect_to_db',return_value=Mock())
    def test_update_null_with_client(self,connect_to_db):
        tester = app.test_client(self)
        test_update_client = { 
            "name": "test_new_client",
            'host_id':1
        }
        test_update_client = json.dumps(test_update_client)
        header={ "Content-Type": "application/json"}
        response = tester.put('/rooms/100',data=test_update_client,headers = header)
        final_output = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(final_output['message'], 'Room does not exist')


    #test successful update 
    @patch('app.connect_to_db',return_value=Mock())
    def test_update_with_client(self,connect_to_db):
        tester = app.test_client(self)
        test_update_client = { 
            "name": "test_update_client",
            "host_id": 2,
        }
        test_update_client = json.dumps(test_update_client)
        header={ "Content-Type": "application/json"}
        response = tester.put('/rooms/10',data=test_update_client,headers = header)
        final_output = json.loads(response.data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(final_output['data']['name'], 'test_update_client')



############### DELETE


    #test delete one room with unmatched
    @patch('app.connect_to_db',return_value=Mock())
    def test_delete_unmacth_with_client(self,connect_to_db):
        tester = app.test_client(self)
        delete_client={'host_id':10}
        delete_client = json.dumps(delete_client)
        header={ "Content-Type": "application/json"}
        response = tester.delete('/rooms/11', data=delete_client,headers = header)
        final_output = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(final_output['message'], 'Action not do valid, host_id not match')


    #test delete one room with empty id
    @patch('app.connect_to_db',return_value=Mock())
    def test_delete_empty_with_client(self,connect_to_db):
        tester = app.test_client(self)
        delete_client={}
        delete_client = json.dumps(delete_client)
        header={ "Content-Type": "application/json"}
        response = tester.delete('/rooms/11', data=delete_client,headers = header)
        final_output = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(final_output['message'], 'No input data provided')


    #test delete one room
    @patch('app.connect_to_db',return_value=Mock())
    def test_delete_with_client(self,connect_to_db):
        tester = app.test_client(self)
        delete_client={'host_id':2}
        delete_client = json.dumps(delete_client)
        header={ "Content-Type": "application/json"}
        response = tester.delete('/rooms/11', data=delete_client,headers = header)
        self.assertEqual(response.status_code, 204)

    




if __name__ == "__main__":
    unittest.main()