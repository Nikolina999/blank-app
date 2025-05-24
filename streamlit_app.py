import streamlit as st
import pandas as pd
import numpy as np
from collections import defaultdict

# Налаштування сторінки з мінімальними вимогами
st.set_page_config(
    page_title="Система рекомендацій книжок",
    page_icon="📚",
    layout="centered"  # використовуємо "centered" замість "wide" для меншого навантаження
)

# Заголовок додатку
st.title("📚 Система рекомендацій української літератури")
st.write("Оптимізована версія для роботи на комп'ютерах з обмеженими ресурсами")

# Завантаження даних - створюємо невеликий набір даних
@st.cache_data
def load_data():
    # Створюємо дані з меншою кількістю користувачів та книжок
    users = [f"користувач_{i}" for i in range(1, 31)]  # скорочуємо до 30 користувачів
    books = [
        "Тіні забутих предків", "Лісова пісня", "Кайдашева сім'я", 
        "Чорна рада", "Захар Беркут", "Земля", "Тигролови",
        "Записки українського самашедшого", "Солодка Даруся", "Місто"
    ]
    
    # Створюємо DataFrame з оцінками
    np.random.seed(42)
    ratings_data = []
    for user in users:
        # Кожен користувач оцінює від 2 до 6 книжок
        num_ratings = np.random.randint(2, 7)
        rated_books = np.random.choice(books, num_ratings, replace=False)
        for book in rated_books:
            # Оцінки від 1 до 5
            rating = np.random.randint(1, 6)
            ratings_data.append({'user_id': user, 'book_title': book, 'rating': rating})
    
    ratings_df = pd.DataFrame(ratings_data)
    
    # Створюємо DataFrame з інформацією про книжки
    books_data = []
    genres = ['Роман', 'Повість', 'Драма', 'Новела', 'Історичний роман']
    authors = ['Михайло Коцюбинський', 'Леся Українка', 'Іван Нечуй-Левицький', 
              'Пантелеймон Куліш', 'Іван Франко', 'Ольга Кобилянська', 'Іван Багряний',
              'Ліна Костенко', 'Марія Матіос', 'Валер\'ян Підмогильний']
    
    # Додаємо конкретну інформацію про книжки
    book_info = {
        "Тіні забутих предків": {"author": "Михайло Коцюбинський", "genre": "Повість", "year": 1911},
        "Лісова пісня": {"author": "Леся Українка", "genre": "Драма", "year": 1911},
        "Кайдашева сім'я": {"author": "Іван Нечуй-Левицький", "genre": "Повість", "year": 1879},
        "Чорна рада": {"author": "Пантелеймон Куліш", "genre": "Історичний роман", "year": 1857},
        "Захар Беркут": {"author": "Іван Франко", "genre": "Історична повість", "year": 1883},
        "Земля": {"author": "Ольга Кобилянська", "genre": "Роман", "year": 1902},
        "Тигролови": {"author": "Іван Багряний", "genre": "Роман", "year": 1944},
        "Записки українського самашедшого": {"author": "Ліна Костенко", "genre": "Роман", "year": 2010},
        "Солодка Даруся": {"author": "Марія Матіос", "genre": "Роман", "year": 2004},
        "Місто": {"author": "Валер'ян Підмогильний", "genre": "Роман", "year": 1928}
    }
    
    for book in books:
        books_data.append({
            'title': book,
            'author': book_info[book]["author"],
            'genre': book_info[book]["genre"],
            'year': book_info[book]["year"]
        })
    
    books_df = pd.DataFrame(books_data)
    
    return ratings_df, books_df

# Завантажуємо дані
ratings_df, books_df = load_data()

# Функція для отримання рекомендацій - оптимізована версія без побудови повної матриці
def get_recommendations_optimized(target_user, ratings_df, n=3):
    """Отримання рекомендацій з використанням оптимізованого алгоритму"""
    # Отримуємо список книжок, які користувач вже оцінив
    user_books = ratings_df[ratings_df['user_id'] == target_user]['book_title'].tolist()
    
    # Знаходимо користувачів, які оцінили ті самі книжки
    similar_users = []
    for idx, row in ratings_df.iterrows():
        if row['user_id'] != target_user and row['book_title'] in user_books:
            similar_users.append(row['user_id'])
    
    # Видаляємо дублікати
    similar_users = list(set(similar_users))
    
    # Знаходимо книжки, які оцінили схожі користувачі, але не оцінив цільовий користувач
    potential_recommendations = {}
    for user in similar_users:
        # Книжки, які оцінив схожий користувач
        user_rated_books = ratings_df[ratings_df['user_id'] == user]
        
        for idx, row in user_rated_books.iterrows():
            book = row['book_title']
            if book not in user_books:  # якщо цільовий користувач не оцінив цю книжку
                if book not in potential_recommendations:
                    potential_recommendations[book] = []
                potential_recommendations[book].append(row['rating'])
    
    # Розраховуємо середню оцінку для кожної потенційної рекомендації
    final_recommendations = {}
    for book, ratings in potential_recommendations.items():
        if len(ratings) > 0:  # мінімум одна оцінка
            final_recommendations[book] = sum(ratings) / len(ratings)
    
    # Сортуємо рекомендації за оцінкою
    sorted_recommendations = sorted(final_recommendations.items(), key=lambda x: x[1], reverse=True)
    
    # Повертаємо топ-n рекомендацій
    return sorted_recommendations[:n]

# Користувацький інтерфейс у Streamlit
st.sidebar.header("Панель керування")

# Вибираємо тип відображення - використовуємо загальні вкладки для зменшення навантаження на інтерфейс
display_mode = st.sidebar.selectbox(
    "Оберіть розділ:",
    ["Рекомендації", "Дані", "Про систему"]
)

if display_mode == "Рекомендації":
    st.header("Отримати рекомендації")
    
    # Вибір користувача
    users_list = sorted(ratings_df['user_id'].unique())
    selected_user = st.selectbox("Оберіть користувача:", users_list)
    
    # Кількість рекомендацій - обмежуємо максимальне значення
    num_recommendations = st.slider("Кількість рекомендацій:", 1, 5, 3)
    
    if st.button("Отримати рекомендації"):
        with st.spinner("Розрахунок рекомендацій..."):
            # Отримуємо рекомендації
            recommendations = get_recommendations_optimized(selected_user, ratings_df, n=num_recommendations)
            
            if recommendations:
                st.subheader(f"Рекомендації для {selected_user}:")
                
                # Створюємо просту таблицю рекомендацій
                rec_data = []
                for book, score in recommendations:
                    book_info = books_df[books_df['title'] == book].iloc[0]
                    rec_data.append({
                        'Назва': book,
                        'Автор': book_info['author'],
                        'Жанр': book_info['genre'],
                        'Прогнозована оцінка': round(score, 1)
                    })
                
                rec_df = pd.DataFrame(rec_data)
                st.dataframe(rec_df)
                
            else:
                st.warning("Не вдалося сформувати рекомендації для цього користувача. Спробуйте обрати іншого.")
    
    # Показуємо книжки, які користувач вже оцінив
    st.subheader(f"Книжки, вже оцінені користувачем {selected_user}:")
    user_ratings = ratings_df[ratings_df['user_id'] == selected_user]
    
    if not user_ratings.empty:
        # Об'єднуємо з інформацією про книжки
        user_books = pd.merge(user_ratings, books_df, left_on='book_title', right_on='title')
        st.dataframe(user_books[['title', 'author', 'genre', 'year', 'rating']])
    else:
        st.info("Користувач ще не оцінив жодної книжки.")

elif display_mode == "Дані":
    st.header("Дані системи")
    
    st.subheader("Інформація про книжки")
    st.dataframe(books_df.rename(columns={
        'title': 'Назва',
        'author': 'Автор',
        'genre': 'Жанр',
        'year': 'Рік'
    }))
    
    st.subheader("Статистика оцінок")
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Всього користувачів", len(ratings_df['user_id'].unique()))
        st.metric("Всього книжок", len(ratings_df['book_title'].unique()))
    
    with col2:
        st.metric("Всього оцінок", len(ratings_df))
        st.metric("Середня оцінка", round(ratings_df['rating'].mean(), 2))
    
    # Замість складних графіків показуємо просту таблицю з розподілом оцінок
    st.subheader("Розподіл оцінок")
    rating_counts = ratings_df['rating'].value_counts().sort_index().reset_index()
    rating_counts.columns = ['Оцінка', 'Кількість']
    st.dataframe(rating_counts)


# Додаємо мінімальний підвал
st.sidebar.markdown("---")
st.sidebar.markdown("📚 **Система рекомендацій української літератури**")


