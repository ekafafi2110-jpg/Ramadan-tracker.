import streamlit as st
import os
from datetime import date, timedelta

# ==========================================
# إعدادات الصفحة (يجب أن تكون أول سطر)
# ==========================================
st.set_page_config(page_title="متابعة رمضان", page_icon="🌙", layout="centered")

# ==========================================
# إعدادات التاريخ
# ==========================================
ramadan_start = date(2026, 2, 19)
today = date.today()
diff = today - ramadan_start
current_ramadan_day = diff.days + 1
FILE_NAME = "my_ramadan_log.txt"

# ==========================================
# قراءة وتحليل البيانات (تجهيزها للوحة التحكم)
# ==========================================
data_list = []
fasting_count = 0
missed_count = 0

if os.path.exists(FILE_NAME):
    with open(FILE_NAME, "r", encoding="utf-8") as file:
        lines = file.readlines()
        for line in lines:
            parts = line.strip().split(" | ")
            if len(parts) == 3:
                date_str, ramadan_day_str, status = parts
                # استخراج رقم اليوم لترتيب الجدول
                day_num = int(ramadan_day_str.replace(" رمضان", "").strip())
                
                # تنسيق الحالة لتكون أجمل
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

# ترتيب البيانات من اليوم الأول إلى الأخير
data_list = sorted(data_list, key=lambda x: x["اليوم"])
# القائمة النهائية للعرض في الجدول
display_list = [{"اليوم في رمضان": d["اليوم في رمضان"], "الحالة": d["الحالة"], "التاريخ الميلادي": d["التاريخ الميلادي"]} for d in data_list]


# ==========================================
# تصميم واجهة الويب (الاحترافية)
# ==========================================
st.title("🌙 نظام متابعة شهر رمضان")
st.caption(f"📅 تاريخ اليوم: {today} | نحن الآن في يوم: {current_ramadan_day} رمضان")

st.markdown("---")

# تقسيم الشاشة إلى 3 تبويبات (Tabs)
tab1, tab2, tab3 = st.tabs(["📝 تسجيل اليوم", "📊 لوحة البيانات والتقارير", "⚙️ إدارة السجلات"])

# ----------------------------------
# التبويب الأول: تسجيل اليوم
# ----------------------------------
with tab1:
    st.subheader("إضافة سجل جديد")
    days_list = [str(i) for i in range(1, 31)]
    default_index = current_ramadan_day - 1 if 1 <= current_ramadan_day <= 30 else 0
    
    selected_day_str = st.selectbox("📌 اختر اليوم الذي تريد تسجيله:", days_list, index=default_index)
    selected_day = int(selected_day_str)

    # جعل الأزرار بجانب بعضها لتوفير المساحة
    status_input = st.radio("❓ ما هي حالة هذا اليوم؟", ["صائم", "مفطر"], horizontal=True)

    if st.button("💾 حفظ السجل", use_container_width=True):
        selected_date = ramadan_start + timedelta(days=selected_day - 1)
        # التحقق من التكرار
        is_already_registered = any(d["اليوم"] == selected_day for d in data_list)
        
        if is_already_registered:
            st.error(f"⚠️ لقد قمت بتسجيل حالة اليوم ({selected_day} رمضان) مسبقاً. اذهب لتبويب 'إدارة السجلات' لحذفه أولاً.")
        else:
            with open(FILE_NAME, "a", encoding="utf-8") as file:
                file.write(f"{selected_date} | {selected_day} رمضان | {status_input}\n")
            st.success(f"✅ تم التسجيل بنجاح!")
            st.rerun() # لتحديث الصفحة فوراً

# ----------------------------------
# التبويب الثاني: لوحة البيانات والتقارير
# ----------------------------------
with tab2:
    st.subheader("📊 ملخص الأداء")
    
    # استخدام بطاقات الأرقام (Metrics) لتبدو احترافية
    col1, col2, col3 = st.columns(3)
    col1.metric("أيام تم تسجيلها", len(data_list))
    col2.metric("✅ أيام الصيام", fasting_count)
    col3.metric("🔴 أيام للقضاء", missed_count)
    
    st.markdown("---")
    st.subheader("📋 جدول السجلات التفصيلي")
    
    if display_list:
        # عرض البيانات في جدول أنيق جداً 
        st.dataframe(display_list, use_container_width=True, hide_index=True)
    else:
        st.info("لا توجد بيانات مسجلة حتى الآن. ابدأ بتسجيل أيامك من التبويب الأول!")

# ----------------------------------
# التبويب الثالث: إدارة السجلات (التعديل/الحذف)
# ----------------------------------
with tab3:
    st.subheader("⚙️ تصحيح الأخطاء")
    st.write("إذا أدخلت حالة يوم بالخطأ، اختره من القائمة لحذفه ثم أعد تسجيله.")
    
    if data_list:
        # إظهار الأيام المسجلة فقط في قائمة الحذف وليس كل الأيام
        registered_days = [str(d["اليوم"]) for d in data_list]
        day_to_delete = st.selectbox("🗑️ اختر اليوم المراد حذفه:", registered_days)
        
        # استخدام زر بلون مختلف للتحذير (primary)
        if st.button("❌ تأكيد حذف السجل", type="primary"):
            with open(FILE_NAME, "r", encoding="utf-8") as file:
                saved_lines = file.readlines()
            
            # الاحتفاظ بكل الأسطر ما عدا السطر الخاص باليوم المحدد
            new_lines = [line for line in saved_lines if f"| {day_to_delete} رمضان |" not in line]
            
            with open(FILE_NAME, "w", encoding="utf-8") as file:
                file.writelines(new_lines)
            
            st.success(f"✅ تم حذف سجل يوم {day_to_delete} رمضان بنجاح!")
            st.rerun() # تحديث الصفحة فوراً ليعكس التعديل
    else:
        st.info("لا توجد سجلات لحذفها.")
