import streamlit as st
import requests
import base64
import pandas as pd
import plotly.express as px
from datetime import date, timedelta

# ==========================================
# إعدادات الصفحة
# ==========================================
st.set_page_config(page_title="متابعة رمضان", page_icon="🌙", layout="centered")

try:
    GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
    GITHUB_REPO = st.secrets["GITHUB_REPO"]
except:
    st.error("⚠️ تأكد من إضافة GITHUB_TOKEN و GITHUB_REPO في Secrets.")
    st.stop()

FILE_PATH = "my_ramadan_log.txt"
ramadan_start = date(2026, 2, 19)
today = date.today()
diff = today - ramadan_start
current_ramadan_day = diff.days + 1

# ==========================================
# دوال الاتصال مع GitHub
# ==========================================
def get_database():
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        content = base64.b64decode(response.json()['content']).decode('utf-8')
        return content.splitlines(), response.json()['sha']
    return [], None

def save_to_database(lines, sha, message="Update"):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    content_str = "\n".join(lines) + ("\n" if lines else "")
    content_b64 = base64.b64encode(content_str.encode('utf-8')).decode('utf-8')
    data = {"message": message, "content": content_b64}
    if sha: data["sha"] = sha
    response = requests.put(url, headers=headers, json=data)
    return response.status_code in [200, 201]

# ==========================================
# معالجة البيانات
# ==========================================
saved_lines, current_sha = get_database()
data_list = []
fasting_count = 0
missed_count = 0

for line in saved_lines:
    if " | " in line:
        parts = line.strip().split(" | ")
        if len(parts) == 3:
            d_str, ram_str, stat = parts
            day_n = int(ram_str.replace(" رمضان", "").strip())
            data_list.append({"اليوم": day_n, "التاريخ": d_str, "الحالة_نص": stat})
            if "صائم" in stat: fasting_count += 1
            else: missed_count += 1

data_list = sorted(data_list, key=lambda x: x["اليوم"])

# ==========================================
# واجهة الويب
# ==========================================
st.title("🌙 نظام متابعة شهر رمضان")
st.caption(f"📅 اليوم: {current_ramadan_day} رمضان")

tab1, tab2, tab3 = st.tabs(["📝 تسجيل", "📊 التقارير", "⚙️ الإدارة"])

with tab1:
    st.subheader("إضافة سجل")
    selected_day = st.selectbox("📌 اختر اليوم:", [str(i) for i in range(1, 31)], index=max(0, min(current_ramadan_day-1, 29)))
    status_input = st.radio("❓ الحالة:", ["صائم", "مفطر"], horizontal=True)
    if st.button("💾 حفظ", use_container_width=True):
        if any(d["اليوم"] == int(selected_day) for d in data_list):
            st.error("⚠️ مسجل مسبقاً!")
        else:
            new_line = f"{ramadan_start + timedelta(days=int(selected_day)-1)} | {selected_day} رمضان | {status_input}"
            saved_lines.append(new_line)
            if save_to_database(saved_lines, current_sha):
                st.success("✅ تم الحفظ!")
                st.rerun()

with tab2:
    st.subheader("📊 إحصائيات الأداء")
    col1, col2 = st.columns(2)
    col1.metric("✅ أيام الصيام", fasting_count)
    col2.metric("🔴 أيام القضاء", missed_count)

    if data_list:
        # --- إضافة الرسم البياني الدائري ---
        st.markdown("---")
        st.write("📈 توزيع الحالة:")
        
        df_chart = pd.DataFrame({
            "الحالة": ["صيام", "قضاء"],
            "الأيام": [fasting_count, missed_count]
        })
        
        # رسم دائري تفاعلي
        fig = px.pie(df_chart, values='الأيام', names='الحالة', 
                     color='الحالة',
                     color_discrete_map={'صيام':'#2ecc71', 'قضاء':'#e74c3c'},
                     hole=0.4) # يجعلها بشكل دونات
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        st.write("📋 السجلات:")
        st.dataframe(data_list, use_container_width=True, hide_index=True)
    else:
        st.info("لا توجد بيانات للعرض.")

with tab3:
    st.subheader("⚙️ حذف السجلات")
    if data_list:
        day_del = st.selectbox("🗑️ حذف يوم:", [str(d["اليوم"]) for d in data_list])
        if st.button("❌ تأكيد الحذف", type="primary"):
            new_lines = [l for l in saved_lines if f"| {day_del} رمضان |" not in l]
            if save_to_database(new_lines, current_sha):
                st.success("✅ تم الحذف")
                st.rerun()
