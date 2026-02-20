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

# 1. إدخال البيانات
days_list = [str(i) for i in range(1, 31)]
default_index = current_ramadan_day - 1 if 1 <= current_ramadan_day <= 30 else 0
selected_day_str = st.selectbox("📌 اختر اليوم الذي تريد تسجيله:", days_list, index=default_index)
selected_day = int(selected_day_str)

status = st.radio("❓ ما هي حالة هذا اليوم؟", ["صائم", "مفطر"])

# زر الحفظ مع منع التكرار
if st.button("💾 حفظ السجل"):
    selected_date = ramadan_start + timedelta(days=selected_day - 1)
    is_already_registered = False
    
    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, "r", encoding="utf-8") as file:
            lines = file.readlines()
            for line in lines:
                if f"| {selected_day} رمضان |" in line:
                    is_already_registered = True
                    break
                    
    if is_already_registered:
        st.error(f"⚠️ لقد قمت بتسجيل حالة اليوم ({selected_day} رمضان) مسبقاً. إذا كان هناك خطأ، قم بحذفه من الأسفل أولاً.")
    else:
        with open(FILE_NAME, "a", encoding="utf-8") as file:
            file.write(f"{selected_date} | {selected_day} رمضان | {status}\n")
        st.success(f"✅ تم تسجيل أنك ({status}) في يوم {selected_day} رمضان بنجاح!")

st.markdown("---")

# 2. التقرير
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

st.markdown("---")

# ==========================================
# 3. إدارة قاعدة البيانات (الجزء الجديد)
# ==========================================
st.subheader("⚙️ إدارة قاعدة البيانات")
st.write("هنا يمكنك رؤية كل ما تم تسجيله، وحذف الإدخالات الخاطئة لتعديلها.")

if os.path.exists(FILE_NAME):
    with open(FILE_NAME, "r", encoding="utf-8") as file:
        saved_lines = file.readlines()
        
    if saved_lines:
        # عرض البيانات للمستخدم بشكل أنيق
        st.markdown("**السجلات الحالية:**")
        for line in saved_lines:
            st.code(line.strip()) # يعرض السطر ككود برمجي ليكون واضحاً
            
        st.markdown("---")
        # حذف سجل (طريقة التعديل)
        day_to_delete = st.selectbox("🗑️ اختر اليوم الذي تريد حذفه لتصحيحه:", days_list, key="delete_select")
        
        if st.button("❌ حذف سجل هذا اليوم"):
            # نقوم بنسخ كل الأسطر باستثناء السطر الذي يحتوي على اليوم المراد حذفه
            new_lines = [line for line in saved_lines if f"| {day_to_delete} رمضان |" not in line]
            
            if len(new_lines) == len(saved_lines):
                st.warning(f"اليوم {day_to_delete} غير مسجل أصلاً في قاعدة البيانات.")
            else:
                # نفتح الملف ونمسح كل شيء، ثم نكتب الأسطر الجديدة فقط
                with open(FILE_NAME, "w", encoding="utf-8") as file:
                    file.writelines(new_lines)
                st.success(f"✅ تم حذف سجل يوم {day_to_delete} بنجاح! سيتم تحديث الصفحة الآن...")
                # أمر لإعادة تحميل الصفحة تلقائياً لترى التغيير فوراً
                st.rerun()
    else:
        st.info("قاعدة البيانات فارغة.")
else:
    st.info("ملف قاعدة البيانات غير موجود بعد.")
