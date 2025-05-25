import requests
import streamlit as st
from typing import Optional, Dict, Any

# バックエンドAPIのベースURL
API_BASE_URL = "http://localhost:8000"

def login_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    """
    ユーザーログイン処理
    
    Args:
        username: ユーザー名
        password: パスワード
    
    Returns:
        成功時: {"access_token": str, "token_type": str}
        失敗時: None
    """
    try:
        response = requests.post(
            f"{API_BASE_URL}/token",
            data={
                "username": username,
                "password": password
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return None
            
    except requests.exceptions.RequestException:
        return None

def get_current_user(token: str) -> Optional[Dict[str, Any]]:
    """
    現在のユーザー情報を取得
    
    Args:
        token: アクセストークン
    
    Returns:
        成功時: ユーザー情報辞書
        失敗時: None
    """
    try:
        response = requests.get(
            f"{API_BASE_URL}/users/me/",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return None
            
    except requests.exceptions.RequestException:
        return None

def is_authenticated() -> bool:
    """
    認証状態をチェック
    
    Returns:
        認証済みの場合True、未認証の場合False
    """
    return "access_token" in st.session_state and st.session_state.access_token is not None

def logout():
    """
    ログアウト処理（セッション情報をクリア）
    """
    if "access_token" in st.session_state:
        del st.session_state.access_token
    if "user_info" in st.session_state:
        del st.session_state.user_info
    if "authenticated" in st.session_state:
        del st.session_state.authenticated

def get_auth_header() -> Dict[str, str]:
    """
    認証ヘッダーを取得
    
    Returns:
        認証ヘッダー辞書
    """
    if is_authenticated():
        return {"Authorization": f"Bearer {st.session_state.access_token}"}
    return {}
