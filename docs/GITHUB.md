# Как завершить сдачу через GitHub

У преподавателя принимается публичный репозиторий `fdf-python` и ссылка на
релиз. В архиве сохранены настоящие локальные коммиты и ветки. GitHub PR пока
не созданы. 
Ниже способ создать три настоящих PR из уже подготовленных этапов.
Нужны Git, GitHub CLI (`gh`) и ваш аккаунт GitHub. Все команды выполняются
из папки проекта, где лежит `main.py`. Каталог `.git` должен сохраниться при
распаковке. Если он скрыт, это нормально.

## 1 Проверить проект

```text
python -m pip install -r requirements-dev.txt
python -m pytest -q
python -m mypy --strict fdf main.py
python -m ruff check .
git log --oneline --all --decorate
```

Используйте Python своего виртуального окружения. Если преподаватель выдаст
стартовый набор, добавьте его настоящие `tests/test_public.py` и запустите тесты
до публикации. Не перезаписывайте собственные тесты и не выдавайте их за выданные.

## 2 Создать пустой репозиторий

```text
gh auth login
gh repo create fdf-python --public --source . --remote origin
git push origin refs/tags/scaffold:refs/heads/main
```

Команда создания выполняется без `--push`. Если репозиторий с таким именем
уже существует, остановитесь и выберите его осознанно: не удаляйте и не
перезаписывайте чужое содержимое. Для уже существующего проекта сначала
проверьте его состояние отдельно.

Почему отправляется `scaffold`: локальная main уже содержит весь проект.
Если сразу отправить готовую main, в следующих PR не будет требуемых
изменений. Тег scaffold указывает на запускаемую первоначальную заготовку.

## 3 Влить парсер

```text
git push origin feature/parser
gh pr create --base main --head feature/parser --title "Добавить модель и парсер карты" --body-file docs/pr_parser.md
gh pr merge feature/parser --merge
```

Дождитесь успешного слияния. Режим `--merge` сохраняет историю этапа;
не используйте squash в этом сценарии.

## 4 Влить проекцию и интерфейс

```text
git push origin feature/render
gh pr create --base main --head feature/render --title "Добавить проекцию и графическое окно" --body-file docs/pr_render.md
gh pr merge feature/render --merge
```

## 5 Влить дополнительные возможности и документацию

```text
git push origin bonus/controls
gh pr create --base main --head bonus/controls --title "Добавить управление цвет и проверки CI" --body-file docs/pr_bonus.md
```

Дождитесь зелёной проверки Actions в браузере, затем:

```text
gh pr merge bonus/controls --merge
gh release create v1.0 --target main --title "FdF v1.0" --notes-file docs/release_notes.md
gh repo view --web
```

Релиз создаётся на удалённой main после трёх слияний. Локальный тег v1.0
обозначает ту же версию содержимого до GitHub merge-коммитов; отдельно
отправлять его не нужно. Не выполняйте `git push --all` или `git push --tags`
до завершения этих шагов.

## 6 Проверить сдачу

В GitHub должны отображаться: публичный репозиторий, не менее пяти коммитов,
три **Merged** PR с содержательными описаниями, успешный workflow Quality,
README со снимком приложения и релиз v1.0. Откройте страницу Releases,
скопируйте ссылки на репозиторий и релиз и передайте преподавателю.
Наличие файла ci.yml само по себе не доказывает прохождение Actions.

Если GitHub требует проверки, запрещает merge или CLI сообщает об ошибке,
не продолжайте следующие шаги до её решения. Публикация не заменяет понимание
кода: на защите могут попросить изменить конкретную функцию.
