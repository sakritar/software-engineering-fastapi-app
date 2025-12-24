## Настройка окружения python

#### Cоздание папки для виртуального окружения

```bash
python -m venv venv
```

#### Активация venv
```bash
source venv/bin/activate
```  

#### Обновление pip
```bash
python -m pip install --upgrade pip
```

#### Установка зависимостей
```bash
python -m pip install --upgrade -r requirements.txt
```

#### Inline
```bash
python -m venv venv && source venv/bin/activate && python -m pip install --upgrade pip && python -m pip install --upgrade -r requirements.txt

python3 -m venv venv && source venv/bin/activate && python3 -m pip install --upgrade pip && python3 -m pip install --upgrade -r requirements.txt
```
