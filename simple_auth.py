import streamlit as st
import os
import json
import hashlib
from datetime import datetime

class SimpleUserManager:
    def __init__(self, config_path='./users.json'):
        self.config_path = config_path
        # 설정 파일이 없는 경우 기본 설정으로 생성
        if not os.path.exists(config_path):
            self._create_default_config()
        self.users = self._load_config()
        
    def _create_default_config(self):
        # 기본 설정 파일 생성 (admin/admin 계정)
        default_config = {
            "admin": {
                "name": "관리자",
                "password": self._hash_password("admin"),
                "email": "admin@example.com",
                "stocks": []
            }
        }
        
        with open(self.config_path, 'w', encoding='utf-8') as file:
            json.dump(default_config, file, ensure_ascii=False, indent=4)
    
    def _load_config(self):
        # 설정 파일 로드
        with open(self.config_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    
    def save_config(self):
        # 설정 파일 저장
        with open(self.config_path, 'w', encoding='utf-8') as file:
            json.dump(self.users, file, ensure_ascii=False, indent=4)
    
    def _hash_password(self, password):
        # 비밀번호 해싱 (간단한 SHA-256 사용)
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register_user(self, username, name, email, password):
        # 사용자 등록
        if username in self.users:
            return False, "이미 존재하는 사용자명입니다."
        
        self.users[username] = {
            'name': name,
            'email': email,
            'password': self._hash_password(password),
            'stocks': []
        }
        self.save_config()
        return True, "등록이 완료되었습니다."
    
    def verify_user(self, username, password):
        # 사용자 인증
        if username not in self.users:
            return False
        
        hashed_password = self._hash_password(password)
        return self.users[username]['password'] == hashed_password
    
    def get_user_name(self, username):
        # 사용자 이름 가져오기
        if username in self.users:
            return self.users[username]['name']
        return None
    
    def save_user_stocks(self, username, stocks):
        # 사용자의 주식 정보 저장
        if username in self.users:
            self.users[username]['stocks'] = stocks
            self.save_config()
            return True
        return False
    
    def get_user_stocks(self, username):
        # 사용자의 주식 정보 조회
        if username in self.users:
            return self.users[username].get('stocks', [])
        return []

# 로그인 함수
def login_user(user_manager):
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'name' not in st.session_state:
        st.session_state.name = None
    
    # 이미 인증된 경우
    if st.session_state.authenticated:
        return True
    
    # 로그인 폼
    with st.form("login_form"):
        username = st.text_input("사용자명")
        password = st.text_input("비밀번호", type="password")
        submit = st.form_submit_button("로그인")
        
        if submit:
            if user_manager.verify_user(username, password):
                st.session_state.authenticated = True
                st.session_state.username = username
                st.session_state.name = user_manager.get_user_name(username)
                return True
            else:
                st.error("아이디 또는 비밀번호가 올바르지 않습니다.")
                return False
    
    return False

# 로그아웃 함수
def logout_user():
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.name = None
    return True

# 회원가입 폼
def register_form(user_manager):
    with st.form("registration_form"):
        new_username = st.text_input('사용자명 (로그인 ID)')
        new_name = st.text_input('이름')
        new_email = st.text_input('이메일')
        new_password = st.text_input('비밀번호', type='password')
        new_password_repeat = st.text_input('비밀번호 확인', type='password')
        
        submit_button = st.form_submit_button('회원가입')
        
        if submit_button:
            if not new_username or not new_name or not new_email or not new_password:
                st.error('모든 필드를 입력해주세요.')
                return False
            elif new_password != new_password_repeat:
                st.error('비밀번호가 일치하지 않습니다.')
                return False
            else:
                success, message = user_manager.register_user(new_username, new_name, new_email, new_password)
                if success:
                    st.success(message)
                    st.info('이제 로그인 탭에서 로그인할 수 있습니다.')
                    return True
                else:
                    st.error(message)
                    return False
    return False 