import streamlit as st
import pickle
import os
from pathlib import Path
import yaml
import bcrypt
import streamlit_authenticator as stauth
from datetime import datetime

# 사용자 관리를 위한 클래스
class UserManager:
    def __init__(self, config_path='./config.yaml'):
        self.config_path = config_path
        # 설정 파일이 없는 경우 기본 설정으로 생성
        if not os.path.exists(config_path):
            self._create_default_config()
        self.config = self._load_config()
        
    def _create_default_config(self):
        # 기본 설정 파일 생성
        default_config = {
            'credentials': {
                'usernames': {
                    'admin': {
                        'email': 'admin@example.com',
                        'name': '관리자',
                        'password': self._hash_password('admin'),
                        'stocks': []
                    }
                }
            },
            'cookie': {
                'expiry_days': 30,
                'key': 'dividend_calculator_cookie',
                'name': 'dividend_calculator_auth'
            },
            'preauthorized': {
                'emails': []
            }
        }
        
        with open(self.config_path, 'w') as file:
            yaml.dump(default_config, file, default_flow_style=False)
    
    def _load_config(self):
        # 설정 파일 로드
        with open(self.config_path, 'r') as file:
            return yaml.safe_load(file)
    
    def save_config(self):
        # 설정 파일 저장
        with open(self.config_path, 'w') as file:
            yaml.dump(self.config, file, default_flow_style=False)
    
    def _hash_password(self, password):
        # 비밀번호 해싱
        return stauth.Hasher([password]).generate()[0]
    
    def register_user(self, username, name, email, password):
        # 사용자 등록
        if username in self.config['credentials']['usernames']:
            return False, "이미 존재하는 사용자명입니다."
        
        self.config['credentials']['usernames'][username] = {
            'email': email,
            'name': name,
            'password': self._hash_password(password),
            'stocks': []
        }
        self.save_config()
        return True, "등록이 완료되었습니다."
    
    def save_user_stocks(self, username, stocks):
        # 사용자의 주식 정보 저장
        if username in self.config['credentials']['usernames']:
            self.config['credentials']['usernames'][username]['stocks'] = stocks
            self.save_config()
            return True
        return False
    
    def get_user_stocks(self, username):
        # 사용자의 주식 정보 조회
        if username in self.config['credentials']['usernames']:
            return self.config['credentials']['usernames'][username].get('stocks', [])
        return []

# 인증 관리자 생성
def create_authenticator():
    user_manager = UserManager()
    config = user_manager.config
    
    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
        config['preauthorized']
    )
    
    return authenticator, user_manager 