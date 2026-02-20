import streamlit as st
import os
from datetime import date, timedelta

# ==========================================
# إعدادات التاريخ
# ==========================================
ramadan_start = date(2026, 2, 19)
today = date.today()
diff = today - ramadan_start
current_ramadan_day = diff.days + 1
FILE_NAME = "my_ramadan_log.txt"

# ==========================================
# تصميم واجهة الويب
# ==========================================
st.title("🌙 نظام متابعة شهر رمضان")
st.subheader(f"📅 نحن اليوم في: {current_ramadan_day} رمضان")

st.markdown("---")

# 1. قائمة منسدلة لاختيار اليوم
days_list = [str(i) for i in range(1, 31)]
default_index = current_ramadan_day - 1 if 1 <= current_ramadan_day <= 30 else 0
selected_day_str = st.selectbox("📌 اختر اليوم الذي تريد تسجيله:", days_list, index=default_index)
selected_day = int(selected_day_str)

# 2. أزرار اختيار الحالة
status = st.radio("❓ ما هي حالة هذا اليوم؟", ["صائم", "مفطر"])

# 3. زر الحفظ مع ميزة منع التكرار
if st.button("💾 حفظ السجل"):
    selected_date = ramadan_start + timedelta(days=selected_day - 1)
    
    # --- بداية التعديل: فحص التكرار ---
    is_already_registered = False
    
    # نتحقق أولاً إذا كان الملف موجوداً لكي نقرأه
    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, "r", encoding="utf-8") as file:
            lines = file.readlines()
            for line in lines:
                # إذا وجدنا رقم اليوم في أي سطر، نعتبره مسجلاً
                if f"| {selected_day} رمضان |" in line:
                    is_already_registered = True
                    break # نوقف البحث لأنه وجد اليوم بالفعل
                    
    # الآن نتخذ القرار بناءً على الفحص
    if is_already_registered:
        st.error(f"⚠️ عذراً! لقد قمت بتسجيل حالة اليوم ({selected_day} رمضان) مسبقاً.")
    else:
        # إذا لم يكن مسجلاً، نقوم بحفظه بشكل طبيعي
        with open(FILE_NAME, "a", encoding="utf-8") as file:
            file.write(f"{selected_date} | {selected_day} رمضان | {status}\n")
        st.success(f"✅ تم تسجيل أنك ({status}) في يوم {selected_day} رمضان بنجاح!")
    # --- نهاية التعديل ---

st.markdown("---")

# 4. زر عرض التقرير
if st.button("📊 عرض تقرير القضاء"):
    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, "r", encoding="utf-8") as file:
            data = file.readlines()
        
        missed_count = 0
        for line in data:
            if "مفطر" in line:
                missed_count += 1
        
        if missed_count > 0:
            st.warning(f"🔴 إجمالي أيام الإفطار التي تحتاج لقضاء: {missed_count} يوم.")
        else:
            st.success("🌟 ممتاز! لا يوجد أيام إفطار مسجلة.")
    else:
        st.info("📁 لا توجد بيانات مسجلة حتى الآن.")
