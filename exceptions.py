class EmptyException(Exception):
    def __str__(self):
        return f"Команда завершена или встречена пустая команда"

