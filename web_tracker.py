import streamlit as st
import requests
import base64
from datetime import date, timedelta

# ==========================================
# إعدادات الصفحة
# ==========================================
st.set_page_config(page_title="متابعة رمضان", page_icon="🌙", layout="centered")

# ==========================================
# جلب المفاتيح السرية من Streamlit
# ==========================================
try:
    GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
    GITHUB_REPO = st.secrets["GITHUB_REPO"]
except:
    st.error("⚠️ يبدو أنك لم تقم بإضافة المفاتيح السرية في إعدادات Streamlit.")
    st.stop()

FILE_PATH = "my_ramadan_log.txt"
ramadan_start = date(2026, 2, 19)
today = date.today()
diff = today - ramadan_start
current_ramadan_day = diff.days + 1

# ==========================================
# دوال الاتصال بقاعدة البيانات (GitHub API)
# ==========================================
def get_database():
    """جلب البيانات من ملف GitHub"""
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        # فك تشفير البيانات لأنها محفوظة بصيغة Base64
        content = base64.b64decode(response.json()['content']).decode('utf-8')
        return content.splitlines(), response.json()['sha']
    elif response.status_code == 404:
        return [], None # الملف غير موجود بعد
    else:
        return [], None

def save_to_database(lines, sha, message="تحديث سجلات رمضان"):
    """حفظ البيانات الجديدة في ملف GitHub"""
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    
    content_str = "\n".join(lines) + ("\n" if lines else "")
    content_b64 = base64.b64encode(content_str.encode('utf-8')).decode('utf-8')
    
    data = {"message": message, "content": content_b64}
    if sha:
        data["sha"] = sha # رقم النسخة الحالية لتأكيد التعديل
        
    response = requests.put(url, headers=headers, json=data)
    return response.status_code in [200, 201]

# ==========================================
# معالجة البيانات للعرض
# ==========================================
saved_lines, current_sha = get_database()

data_list = []
fasting_count = 0
missed_count = 0

for line in saved_lines:
    if " | " in line:
        parts = line.strip().split(" | ")
        if len(parts) == 3:
            date_str, ramadan_day_str, status = parts
            day_num = int(ramadan_day_str.replace(" رمضان", "").strip())
            formatted_status = "✅ صائم" if "صائم" in status else "🔴 مفطر"
            
            data_list.append({
                "اليوم": day_num, 
                "التاريخ الميلادي": date_str, 
                "اليوم في رمضان": ramadan_day_str, 
                "الحالة": formatted_status
            })
            
            if "صائم" in status:
                fasting_count += 1
            elif "مفطر" in status:
                missed_count += 1

data_list = sorted(data_list, key=lambda x: x["اليوم"])
display_list = [{"اليوم في رمضان": d["اليوم في رمضان"], "الحالة": d["الحالة"], "التاريخ الميلادي": d["التاريخ الميلادي"]} for d in data_list]

# ==========================================
# تصميم واجهة الويب
# ==========================================
st.title("🌙 نظام متابعة شهر رمضان")
st.caption(f"📅 تاريخ اليوم: {today} | نحن الآن في يوم: {current_ramadan_day} رمضان")
st.markdown("---")

tab1, tab2, tab3 = st.tabs(["📝 تسجيل اليوم", "📊 لوحة البيانات", "⚙️ إدارة السجلات"])

# --- التبويب الأول ---
with tab1:
    st.subheader("إضافة سجل جديد")
    days_list = [str(i) for i in range(1, 31)]
    default_index = current_ramadan_day - 1 if 1 <= current_ramadan_day <= 30 else 0
    
    selected_day = int(st.selectbox("📌 اختر اليوم الذي تريد تسجيله:", days_list, index=default_index))
    status_input = st.radio("❓ ما هي حالة هذا اليوم؟", ["صائم", "مفطر"], horizontal=True)

    if st.button("💾 حفظ السجل", use_container_width=True):
        selected_date = ramadan_start + timedelta(days=selected_day - 1)
        is_already_registered = any(d["اليوم"] == selected_day for d in data_list)
        
        if is_already_registered:
            st.error(f"⚠️ لقد قمت بتسجيل حالة اليوم ({selected_day} رمضان) مسبقاً.")
        else:
            with st.spinner('جاري الحفظ في قاعدة البيانات السحابية...'):
                new_line = f"{selected_date} | {selected_day} رمضان | {status_input}"
                saved_lines.append(new_line)
                
                if save_to_database(saved_lines, current_sha):
                    st.success("✅ تم الحفظ بنجاح! بياناتك الآن آمنة ولن تضيع.")
                    st.rerun()
                else:
                    st.error("❌ حدث خطأ أثناء الحفظ. تأكد من إعدادات الاتصال.")

# --- التبويب الثاني ---
with tab2:
    st.subheader("📊 ملخص الأداء")
    col1, col2, col3 = st.columns(3)
    col1.metric("أيام مسجلة", len(data_list))
    col2.metric("✅ الصيام", fasting_count)
    col3.metric("🔴 القضاء", missed_count)
    
    st.markdown("---")
    if display_list:
        st.dataframe(display_list, use_container_width=True, hide_index=True)
    else:
        st.info("لا توجد بيانات مسجلة حتى الآن.")

# --- التبويب الثالث ---
with tab3:
    st.subheader("⚙️ تصحيح الأخطاء")
    if data_list:
        registered_days = [str(d["اليوم"]) for d in data_list]
        day_to_delete = st.selectbox("🗑️ اختر اليوم المراد حذفه:", registered_days)
        
        if st.button("❌ تأكيد حذف السجل", type="primary"):
            with st.spinner('جاري الحذف من قاعدة البيانات...'):
                new_lines = [line for line in saved_lines if f"| {day_to_delete} رمضان |" not in line]
                
                if save_to_database(new_lines, current_sha, f"حذف سجل يوم {day_to_delete}"):
                    st.success(f"✅ تم حذف سجل يوم {day_to_delete} بنجاح!")
                    st.rerun()
                else:
                    st.error("❌ حدث خطأ أثناء الحذف.")
    else:
        st.info("قاعدة البيانات فارغة.")
