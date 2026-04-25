import streamlit as st
import pandas as pd

from utils import load_bot_status, load_bot_logs, load_bot_inventory, load_config, save_config, ITEM_INFO
from bot_ctrl import is_bot_process_running, start_bot_process, stop_bot_process, trigger_remote_command

def render_sidebar(bot_is_running):
    """渲染 Streamlit 側邊欄的機器人控制中心。"""
    st.sidebar.title("🎮 機器人控制中心")
    
    status_color = "🟢 運行中" if bot_is_running else "🔴 已停止"
    st.sidebar.write(f"當前狀態：{status_color}")

    if st.sidebar.button("🚀 啟動機器人", use_container_width=True, disabled=bot_is_running):
        result = start_bot_process()
        if result["success"]:
            st.session_state.bot_process_pid = result["pid"]
            st.toast("機器人已啟動！")
        else:
            st.error(result["message"])
        st.rerun()

    if st.sidebar.button("🛑 停止機器人", use_container_width=True, disabled=not bot_is_running):
        result = stop_bot_process(st.session_state.bot_process_pid)
        if result["success"]:
            st.session_state.bot_process_pid = None
            st.toast("機器人已停止。")
        else:
            st.warning(result["message"])
        st.rerun()

    st.sidebar.divider()
    
    mode = st.sidebar.radio(
        "選擇運作模式：",
        ["自動整理", "庫存管理"],
        help="分類；數據同步。"
    )

def render_main_tabs(bot_is_running):
    """渲染 Streamlit 主介面的各個分頁。"""
    bot_status = load_bot_status()
    current_logs = load_bot_logs()
    current_inventory = load_bot_inventory()
    config = load_config()

    tab1, tab2, tab3, tab4 = st.tabs(["📦 倉庫", "🗺️ 箱子管理", "⚙️ 設定", "📊 Log"])

    with tab1:
        col1, col2 = st.columns([2, 1])
        with col1:
            st.subheader("📦 倉庫概覽")
            if current_inventory:
                st.dataframe(pd.DataFrame(current_inventory), use_container_width=True)
            else:
                st.info("機器人未運行或尚未掃描到庫存數據。")
            
            if st.button("🔄 重新掃描"):
                result = trigger_remote_command("scan", bot_process_pid=st.session_state.bot_process_pid)
                if result["success"]:
                    st.toast("已送出掃描指令")
                else:
                    st.error(result["message"])

        with col2:
            st.subheader("機器人資訊")
            st.info(f"**使用者名稱:** {bot_status['username']}\n\n"
                    f"**座標:** X: {bot_status['coordinates']['x']:.1f}, Y: {bot_status['coordinates']['y']:.1f}, Z: {bot_status['coordinates']['z']:.1f}\n\n"
                    f"**目前任務:** {bot_status['task']}")
            st.progress(bot_status['health'] / 20, text=f"血量 ({bot_status['health']}/20)")
            st.progress(bot_status['food'] / 20, text=f"飽食度 ({bot_status['food']}/20)")

    with tab2:
        st.subheader("📦 箱子區域設定 (Chest View Technology)")
        st.write("在此偵測並定義箱子區域。支援 L 形狀佈局與 2D 視覺化。")
        
        # 箱子區域編輯器
        df_areas = pd.DataFrame(config.get('chest_areas', []))
        edited_areas = st.data_editor(df_areas, num_rows="dynamic", use_container_width=True, key="area_editor")
        
        # 2D 檢視預留空間
        st.divider()
        st.subheader("🖼️ 2D 佈局檢視")
        st.info("💡 這裡將顯示 2D 平面圖，允許點選座標來設定 L 形區域。 (開發中)")
        # 這裡可以放置一個畫布或特定的 Grid 元件
        st.markdown("""
        <div style="height:200px; background-color:#222; border:1px solid #444; display:flex; align-items:center; justify-content:center; color:#666;">
            [ 2D 網格檢視區域預留 ]
        </div>
        """, unsafe_allow_html=True)

    with tab3:
        col_left, col_right = st.columns(2)
        with col_left:
            st.subheader("🌐 伺服器設定")
            config['server']['host'] = st.text_input("伺服器位址 (IP)", config['server']['host'])
            config['server']['port'] = st.number_input("埠號 (Port)", value=config['server']['port'], step=1)
        
        with col_right:
            st.subheader("🤖 AI API 設定")
            config['ai_config']['enabled'] = st.toggle("啟動 AI 決策系統", config['ai_config']['enabled'])
            config['ai_config']['api_key'] = st.text_input("API 金鑰", config['ai_config']['api_key'], type="password")
            st.caption("預留空間：用於整合 LLM 以自動判斷座標與整理邏輯。")
        
        st.divider()
        st.subheader("🛠️ 自動分類規則")
        
        # 準備物品下拉選單資料
        item_options = [f"{v['icon']} {v['name']}" for v in ITEM_INFO.values()]
        area_options = [a['名稱'] for a in edited_areas.to_dict('records')] if not edited_areas.empty else ["未設定"]

        df_rules = pd.DataFrame(config.get('sorting_rules', []))
        
        # 使用 column_config 設定下拉選單
        edited_rules = st.data_editor(
            df_rules, 
            num_rows="dynamic", 
            use_container_width=True,
            column_config={
                "物品": st.column_config.SelectboxColumn(options=item_options, required=True),
                "箱子區域": st.column_config.SelectboxColumn(options=area_options, required=True),
                "模式": st.column_config.SelectboxColumn(options=["一箱子多物品", "一箱子一物品"], required=True)
            }
        )
        
        if st.button("💾 儲存設定"):
            config['sorting_rules'] = edited_rules.to_dict('records')
            config['chest_areas'] = edited_areas.to_dict('records')
            save_config(config)
            st.success("設定檔已成功儲存至 config.json")

    with tab4:
        st.subheader("📜 系統日誌")
        log_content = "\n".join(current_logs[::-1]) if current_logs else "尚無日誌資料..."
        with st.container(border=True, height=300):
            st.code(log_content, language="bash")