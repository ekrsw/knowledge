import streamlit as st
import sys
import os

# パスを追加してutilsモジュールをインポート
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.auth import logout, is_authenticated

def show_dashboard():
    """ダッシュボード画面を表示"""
    
    # ページ設定
    st.set_page_config(
        page_title="ナレッジ投稿システム - ダッシュボード",
        page_icon="📊",
        layout="wide"
    )
    
    # 認証チェック
    if not is_authenticated():
        st.error("ログインが必要です。")
        st.stop()
    
    # カスタムCSS
    st.markdown("""
    <style>
    .dashboard-header {
        background-color: #004a55;
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .welcome-message {
        font-size: 1.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .user-info {
        font-size: 1rem;
        opacity: 0.9;
    }
    .dashboard-card {
        background-color: #fafafa;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    .card-title {
        color: #004a55;
        font-size: 1.2rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .logout-button {
        position: absolute;
        top: 1rem;
        right: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # ヘッダー
    col1, col2 = st.columns([4, 1])
    
    with col1:
        st.markdown('<div class="dashboard-header">', unsafe_allow_html=True)
        if "user_info" in st.session_state:
            user_info = st.session_state.user_info
            st.markdown(f'<div class="welcome-message">ようこそ、{user_info["full_name"]}さん！</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="user-info">ユーザー名: {user_info["username"]} | 管理者: {"はい" if user_info.get("is_admin", False) else "いいえ"}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="welcome-message">ダッシュボード</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        if st.button("ログアウト", key="logout_btn"):
            logout()
            st.success("ログアウトしました。")
            st.rerun()
    
    # メインコンテンツ
    st.markdown("## 📊 システム概要")
    
    # 機能カード
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">📝 ナレッジ投稿</div>', unsafe_allow_html=True)
        st.markdown("新しいナレッジや修正案を投稿できます。")
        if st.button("ナレッジを投稿", key="create_knowledge"):
            st.info("ナレッジ投稿機能は今後実装予定です。")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">📋 ナレッジ一覧</div>', unsafe_allow_html=True)
        st.markdown("投稿されたナレッジを確認・管理できます。")
        if st.button("ナレッジ一覧", key="view_knowledge"):
            st.info("ナレッジ一覧機能は今後実装予定です。")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">📊 統計情報</div>', unsafe_allow_html=True)
        st.markdown("システムの利用状況を確認できます。")
        if st.button("統計を表示", key="view_stats"):
            st.info("統計機能は今後実装予定です。")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 最近の活動
    st.markdown("## 📈 最近の活動")
    st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
    st.info("最近の活動情報は今後実装予定です。")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 管理者専用セクション
    if "user_info" in st.session_state and st.session_state.user_info.get("is_admin", False):
        st.markdown("## 🔧 管理者機能")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
            st.markdown('<div class="card-title">👥 ユーザー管理</div>', unsafe_allow_html=True)
            st.markdown("システムユーザーの管理を行えます。")
            if st.button("ユーザー管理", key="manage_users"):
                st.info("ユーザー管理機能は今後実装予定です。")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
            st.markdown('<div class="card-title">📄 記事管理</div>', unsafe_allow_html=True)
            st.markdown("記事のインポート・管理を行えます。")
            if st.button("記事管理", key="manage_articles"):
                st.info("記事管理機能は今後実装予定です。")
            st.markdown('</div>', unsafe_allow_html=True)
    
    # フッター
    st.markdown("---")
    st.markdown('<p style="text-align: center; color: #999; font-size: 0.8rem;">© 2024 ナレッジ投稿システム</p>', unsafe_allow_html=True)

if __name__ == "__main__":
    show_dashboard()
