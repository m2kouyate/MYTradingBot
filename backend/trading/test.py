import requests
from tqdm import tqdm


def find_closed_chats(webhook_url: str, start_id: int, end_id: int):
    """
    Поиск закрытых групповых чатов типа 'chat'

    Args:
        webhook_url: полный URL вебхука
        start_id: начальный ID
        end_id: конечный ID
    """
    try:
        found_chats = []
        print(f"Ищем закрытые чаты с ID от {start_id} до {end_id}...")

        for chat_id in tqdm(range(start_id, end_id + 1), desc="Сканирование"):
            try:
                response = requests.get(
                    f"{webhook_url}/im.dialog.get.json",
                    params={'DIALOG_ID': f'chat{chat_id}'},
                    timeout=5
                )

                if response.status_code == 200:
                    data = response.json()
                    if data.get('result'):
                        chat_info = data['result']
                        if chat_info.get('type') == 'chat' and chat_info.get('name'):
                            chat_data = {
                                'id': chat_id,
                                'name': chat_info['name'],
                                'owner': chat_info.get('owner'),
                                'date_create': chat_info.get('date_create'),
                                'user_counter': chat_info.get('user_counter', 0),
                                'description': chat_info.get('description', '')
                            }
                            found_chats.append(chat_data)

                            # Получаем список участников
                            users_response = requests.get(
                                f"{webhook_url}/im.dialog.users.get.json",
                                params={'DIALOG_ID': f'chat{chat_id}'}
                            )

                            if users_response.status_code == 200:
                                users_data = users_response.json()
                                chat_data['users'] = users_data.get('result', [])

                            # Выводим информацию о найденном чате
                            print(f"\nНайден закрытый чат:")
                            print(f"ID: chat{chat_id}")
                            print(f"Название: {chat_info['name']}")
                            print(f"Участников: {chat_info.get('user_counter', 0)}")
                            if chat_data.get('users'):
                                print("Участники:")
                                for user in chat_data['users']:
                                    print(f"- {user.get('name')} (ID: {user.get('id')})")

            except requests.Timeout:
                continue
            except requests.RequestException:
                continue

        # Итоговая сводка
        print(f"\nВсего найдено закрытых чатов: {len(found_chats)}")
        for chat in found_chats:
            print(f"\n- {chat['name']} (ID: chat{chat['id']})")
            print(f"  Создан: {chat['date_create']}")
            print(f"  Участников: {chat['user_counter']}")
            if chat.get('users'):
                print("  Участники:")
                for user in chat['users']:
                    print(f"  - {user.get('name')} (ID: {user.get('id')})")

    except Exception as e:
        print(f"Неожиданная ошибка: {e}")


# Пример использования
if __name__ == "__main__":
    WEBHOOK_URL = "https://trophycrm.bitrix24.com/rest/44/jvxm5pe74a8ot206"

    # Сканируем больший диапазон
    start_id = 1000
    end_id = 7000
    find_closed_chats(WEBHOOK_URL, start_id, end_id)