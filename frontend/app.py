import streamlit as st
import sys
import os

# パスを追加してモジュールをインポート
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from utils.auth import is_authenticated
from pages.login import show_login_page
from pages.dashboard import show_dashboard

def main():
    """メインアプリケーション"""
    
    # セッション状態の初期化
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "access_token" not in st.session_state:
        st.session_state.access_token = None
    if "user_info" not in st.session_state:
        st.session_state.user_info = None
    
    # 認証状態に応じてページを表示
    if is_authenticated():
        # ログイン済み - ダッシュボードを表示
        show_dashboard()
    else:
        # 未ログイン - ログイン画面を表示
        show_login_page()

if __name__ == "__main__":
    main()
