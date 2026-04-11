# [实验一](./readme.md)/报告描述：

Arm Memory Tagging Extension (MTE): Аппаратная поддержка обнаружения пространственных и временных ошибок памяти в Armv8.5-A и выше
Arm Memory Tagging Extension (MTE) — аппаратное расширение Armv8.5-A (и Armv9), реализующее механизм lock-and-key для безопасности памяти. Каждые 16 байт памяти получают 4-битный allocation tag (замок), а указатели — logical tag (ключ) в верхнем байте (Top Byte Ignore). При load/store в Normal Tagged Memory процессор автоматически проверяет совпадение тегов и вызывает исключение при несоответствии. MTE поддерживает три режима: Synchronous (SYNC — точное обнаружение), Asynchronous (ASYNC — низкий overhead) и Asymmetric (ASYMM). Это позволяет эффективно выявлять buffer overflow, use-after-free, use-after-return и другие ошибки памяти с минимальными изменениями в аллокаторе и ОС. 

1. Основные принципы MTE: lock-and-key механизм, гранулярность 16 байт, режимы SYNC/ASYNC/ASYMM.
2. Практические способы обнаружения spatial и temporal ошибок памяти с минимальными правками кода.
3. Сравнение overhead MTE с ASan и рекомендации по использованию в тестировании и продакшене.
4. Простые оптимизации и поддержка MTE в Android/Linux.

Источники:
- Armv8.5-A Memory Tagging Extension White Paper (developer.arm.com)
- Android Open Source Project: Arm memory tagging extension
- ARM MTE Performance in Practice (arXiv:2601.11786, 2026)
- Project Zero: MTE As Implemented