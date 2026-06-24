import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="高度ロボット動作解析ツール", layout="wide")
st.title("ロボットデータ・マルチ解析ダッシュボード")

uploaded_file = st.sidebar.file_uploader("CSVファイルをアップロード", type=['csv'])

if uploaded_file is not None:
    # エラー行をスキップしつつ読み込み
    df = pd.read_csv(uploaded_file, on_bad_lines='skip')
    columns = df.columns.tolist()
    st.sidebar.success("データを読み込みました")

    # 1. プリセット（解析モード）の選択
    st.sidebar.header("1. 解析プリセットの選択")
    preset_mode = st.sidebar.selectbox(
        "モードを選択してください",
        ["カスタム（自由配置）", "角度追従評価（目標 vs 現在）", "2D位置軌跡"]
    )

    # 2. グラフの複製・追加コントロール
    st.sidebar.header("2. グラフの追加・複製")
    num_graphs = st.sidebar.number_input("表示するグラフの総数", min_value=1, max_value=6, value=1, step=1)

    # 時間軸の選択（共通で使用することが多いためトップに配置）
    time_col = st.sidebar.selectbox("共通の時間軸 (Time)", columns)

    # メインエリア：指定された数だけグラフを動的に生成
    for i in range(int(num_graphs)):
        st.markdown(f"### 📊 グラフ #{i+1}")
        
        # プリセットに応じたデフォルト値の割り当てロジック
        default_index_x = 0
        default_index_y = [0]
        
        if preset_mode == "角度追従評価（目標 vs 現在）" and i == 0:
            # 1つ目のグラフに角度追従を自動セット（列名が含まれている場合）
            target_opts = [c for c in columns if "目標" in c or "target" in c.lower()]
            current_opts = [c for c in columns if "現在" in c or "imu" in c.lower() or "current" in c.lower()]
            
            st.info("プリセット: 角度追従評価が適用されています（変更も可能です）")
            selected_cols = st.multiselect(
                f"表示する変数 (複数選択可) [グラフ #{i+1}]", 
                columns, 
                default=target_opts + current_opts if (target_opts and current_opts) else columns[:2],
                key=f"cols_preset_{i}"
            )
            
            # 描画
            fig = go.Figure()
            for col in selected_cols:
                fig.add_trace(go.Scatter(x=df[time_col], y=df[col], mode='lines', name=col))
            fig.update_layout(xaxis_title=time_col, yaxis_title="値")
            st.plotly_chart(fig, width='stretch')
            
        elif preset_mode == "2D位置軌跡" and i == 0:
            st.info("プリセット: 2D位置軌跡が適用されています")
            x_opts = [c for c in columns if "x" in c.lower() or "座標" in c]
            y_opts = [c for c in columns if "y" in c.lower() or "座標" in c]
            
            col_x = st.selectbox(f"X軸の変数 [グラフ #{i+1}]", columns, index=columns.index(x_opts[0]) if x_opts else 0, key=f"x_{i}")
            col_y = st.selectbox(f"Y軸の変数 [グラフ #{i+1}]", columns, index=columns.index(y_opts[0]) if y_opts else 0, key=f"y_{i}")
            
            fig_traj = px.line(df, x=col_x, y=col_y, title=f"2D軌跡: {col_x} vs {col_y}")
            fig_traj.update_yaxes(scaleanchor="x", scaleratio=1) # アスペクト比1:1
            st.plotly_chart(fig_traj, width='stretch')
            
        else:
            # カスタムモード、または2つ目以降に複製されたグラフの挙動
            col_type = st.radio(f"グラフの種類 [グラフ #{i+1}]", ["時系列ライングラフ", "2D散布図・軌跡"], key=f"type_{i}", horizontal=True)
            
            if col_type == "時系列ライングラフ":
                selected_cols = st.multiselect(f"表示する変数 (複数選択可) [グラフ #{i+1}]", columns, default=[columns[0]], key=f"mul_{i}")
                fig = go.Figure()
                for col in selected_cols:
                    fig.add_trace(go.Scatter(x=df[time_col], y=df[col], mode='lines', name=col))
                fig.update_layout(xaxis_title=time_col, yaxis_title="値")
                st.plotly_chart(fig, width='stretch')
                
            elif col_type == "2D散布図・軌跡":
                col_x = st.selectbox(f"X軸の変数 [グラフ #{i+1}]", columns, key=f"x_c_{i}")
                col_y = st.selectbox(f"Y軸の変数 [グラフ #{i+1}]", columns, key=f"y_c_{i}")
                fig_traj = px.line(df, x=col_x, y=col_y)
                fig_traj.update_yaxes(scaleanchor="x", scaleratio=1)
                st.plotly_chart(fig_traj, width='stretch')

else:
    st.info("サイドバーからCSVファイルをアップロードすると、マルチ解析ダッシュボードが起動します。")