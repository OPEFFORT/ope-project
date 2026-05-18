import pytest
import mutate

from unittest import mock


@pytest.fixture()
def app():
    with mock.patch('mutate.get_client') as mock_get_client, mock.patch(
        'mutate.get_group_resource'
    ) as mock_get_group_resource, mock.patch(
        'mutate.get_group_members'
    ) as mock_group_members:
        mock_object = mock.Mock()
        mock_get_client.return_value = mock_object
        mock_get_group_resource.return_value = mock_object

        def mock_get_group_members(group_resource, group_name):
            if group_name == 'class1':
                return ['user1']
            elif group_name == 'class2':
                return ['user2']
            return []

        mock_group_members.side_effect = mock_get_group_members

        app = mutate.create_app(GROUPS='class1,class2', LABEL='testlabel')

        app.config.update(
            {
                'TESTING': True,
            }
        )

        yield app


@pytest.fixture()
def client(app):
    return app.test_client()


# Sending empty json request
def test_mutate_bad_data(client):
    res = client.post('/mutate', json={})

    assert res.status_code == 400

    res_json = res.get_json()

    assert 'Invalid request' in res_json['response']['status']['message']


# Calling a bad path
def test_bad_path(client):
    res = client.get('/fake_path')
    assert res.status_code == 404

    assert 'The requested URL was not found' in res.data.decode('utf-8')


# Proper request that contains no metadata
def test_request_no_metadata(client):
    res = client.post(
        '/mutate',
        json={
            'request': {
                'uid': '1234',
                'object': {'metadata': {}},
            }
        },
    )

    assert res.status_code == 200
    assert res.json == {
        'apiVersion': 'admission.k8s.io/v1',
        'kind': 'AdmissionReview',
        'response': {
            'allowed': True,
            'status': {'message': 'No class label assigned.'},
            'uid': '1234',
            'patchType': None,
            'patch': None,
        },
    }


# Exeption response
def test_api_exception(client):
    mutate.get_group_members.side_effect = ValueError('this is a test')
    res = client.post(
        '/mutate',
        json={
            'request': {
                'uid': '1234',
                'object': {
                    'metadata': {
                        'labels': {
                            'opendatahub.io/user': 'testuser1',
                        }
                    }
                },
            }
        },
    )
    assert res.status_code == 500
    assert res.text == 'unexpected error encountered'


# If user1 in group1, returns successful json patch
def test_valid_request(client):
    res = client.post(
        '/mutate',
        json={
            'request': {
                'uid': '1234',
                'object': {
                    'metadata': {
                        'labels': {
                            'opendatahub.io/user': 'user1',
                        }
                    }
                },
            }
        },
    )

    print(f'Response code: {res.status_code}')
    print(f'Response JSON: {res.get_json()}')
    assert res.status_code == 200
    assert res.get_json()['response']['patchType'] == 'JSONPatch'


# Pod has invalid (empty) UID
def test_invalid_uid(client):
    res = client.post(
        '/mutate',
        json={
            'request': {
                'uid': '',
                'object': {
                    'metadata': {
                        'labels': {
                            'opendatahub.io/user': 'user1',
                        }
                    }
                },
            }
        },
    )

    assert res.status_code == 400

    assert 'Invalid request' in res.get_json()['response']['status']['message']


# Request formatted correctly but contains empty or no user
def test_no_user(client):
    res = client.post(
        '/mutate',
        json={
            'request': {
                'uid': '1234',
                'object': {
                    'metadata': {
                        'labels': {
                            'opendatahub.io/user': '',
                        }
                    }
                },
            }
        },
    )

    assert res.status_code == 200
    assert res.json == {
        'apiVersion': 'admission.k8s.io/v1',
        'kind': 'AdmissionReview',
        'response': {
            'allowed': True,
            'status': {'message': 'No class label assigned.'},
            'uid': '1234',
            'patchType': None,
            'patch': None,
        },
    }

    res = client.post(
        '/mutate',
        json={
            'request': {
                'uid': '1234',
                'object': {'metadata': {'labels': {}}},
            }
        },
    )

    assert res.status_code == 200
    assert res.json == {
        'apiVersion': 'admission.k8s.io/v1',
        'kind': 'AdmissionReview',
        'response': {
            'allowed': True,
            'status': {'message': 'No class label assigned.'},
            'uid': '1234',
            'patchType': None,
            'patch': None,
        },
    }


# Valid request but all groups empty
def test_empty_group_members(client):
    with mock.patch('mutate.get_group_members') as mock_group_members:
        mock_group_members.return_value = []
        res = client.post(
            '/mutate',
            json={
                'request': {
                    'uid': '1234',
                    'object': {
                        'metadata': {
                            'labels': {
                                'opendatahub.io/user': 'user1',
                            }
                        }
                    },
                }
            },
        )

        assert res.status_code == 200
        assert res.json == {
            'apiVersion': 'admission.k8s.io/v1',
            'kind': 'AdmissionReview',
            'response': {
                'allowed': True,
                'status': {'message': 'No class label assigned.'},
                'uid': '1234',
                'patchType': None,
                'patch': None,
            },
        }
