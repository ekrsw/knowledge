import streamlit as st
import sys
import os

# パスを追加してutilsモジュールをインポート
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.auth import login_user, get_current_user

def show_login_page():
    """ログイン画面を表示"""
    
    # ページ設定
    st.set_page_config(
        page_title="ナレッジ投稿システム - ログイン",
        page_icon="🔐",
        layout="centered"
    )
    
    # カスタムCSS
    st.markdown("""
    <style>
    .login-container {
        max-width: 400px;
        margin: 0 auto;
        padding: 2rem;
        background-color: #fafafa;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .login-title {
        text-align: center;
        color: #004a55;
        margin-bottom: 2rem;
        font-size: 2rem;
        font-weight: bold;
    }
    .login-form {
        margin-bottom: 1rem;
    }
    .stButton > button {
        width: 100%;
        background-color: #004a55;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        font-weight: bold;
    }
    .stButton > button:hover {
        background-color: #003a44;
    }
    .error-message {
        color: #d32f2f;
        text-align: center;
        margin-top: 1rem;
        padding: 0.5rem;
        background-color: #ffebee;
        border-radius: 5px;
        border-left: 4px solid #d32f2f;
    }
    .success-message {
        color: #2e7d32;
        text-align: center;
        margin-top: 1rem;
        padding: 0.5rem;
        background-color: #e8f5e8;
        border-radius: 5px;
        border-left: 4px solid #2e7d32;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # メインコンテナ
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        
        # タイトル
        st.markdown('<h1 class="login-title">🔐 ログイン</h1>', unsafe_allow_html=True)
        st.markdown('<p style="text-align: center; color: #666; margin-bottom: 2rem;">ナレッジ投稿システムにログインしてください</p>', unsafe_allow_html=True)
        
        # ログインフォーム
        with st.form("login_form"):
            st.markdown('<div class="login-form">', unsafe_allow_html=True)
            
            username = st.text_input(
                "ユーザー名",
                placeholder="ユーザー名を入力してください",
                key="username_input"
            )
            
            password = st.text_input(
                "パスワード",
                type="password",
                placeholder="パスワードを入力してください",
                key="password_input"
            )
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # ログインボタン
            login_button = st.form_submit_button("ログイン")
            
            if login_button:
                if not username or not password:
                    st.markdown('<div class="error-message">ユーザー名とパスワードを入力してください。</div>', unsafe_allow_html=True)
                else:
                    # ログイン処理
                    with st.spinner("ログイン中..."):
                        login_result = login_user(username, password)
                        
                        if login_result:
                            # ログイン成功
                            st.session_state.access_token = login_result["access_token"]
                            st.session_state.authenticated = True
                            
                            # ユーザー情報を取得
                            user_info = get_current_user(login_result["access_token"])
                            if user_info:
                                st.session_state.user_info = user_info
                                st.markdown('<div class="success-message">ログインに成功しました！</div>', unsafe_allow_html=True)
                                st.success(f"ようこそ、{user_info['full_name']}さん！")
                                
                                # 少し待ってからリダイレクト
                                st.balloons()
                                st.rerun()
                            else:
                                st.markdown('<div class="error-message">ユーザー情報の取得に失敗しました。</div>', unsafe_allow_html=True)
                        else:
                            # ログイン失敗
                            st.markdown('<div class="error-message">ユーザー名またはパスワードが正しくありません。</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # フッター
        st.markdown("---")
        st.markdown('<p style="text-align: center; color: #999; font-size: 0.8rem;">© 2024 ナレッジ投稿システム</p>', unsafe_allow_html=True)

if __name__ == "__main__":
    show_login_page()
