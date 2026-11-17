# Ответы на компетентностные вопросы к онтологии League of Legends

Данные Data Dragon 16.20.1 / ru_RU. Эффекты размечены для Кармы, Люкс и Морганы. В таблицах идентификаторы приведены без префикса `lol:`.

## 1. Щит союзнику и контроль передвижения

По размеченным эффектам подходят Карма, Люкс и Моргана. Карма даёт щит выбранному союзнику умением E, замедляет врага попаданием Q и обездвиживает умением W, если связь сохраняется. Люкс даёт щит умением W при касании союзника жезлом, обездвиживает попаданием Q и замедляет врагов в области E. Моргана даёт выбранному союзнику щит от магического урона умением E, обездвиживает первого врага, поражённого Q, и замедляет связанного цепью врага умением R. Если цепь сохраняется до конца задержки, R также оглушает.

```sparql
PREFIX lol: <https://example.org/lol-ontology#>
SELECT DISTINCT ?champion ?name ?shieldAbility ?shieldCondition
                ?controlAbility ?controlMechanic ?controlCondition
WHERE {
  ?champion a lol:Champion ; lol:name ?name ;
            lol:hasCategory lol:Category_Mage ;
            lol:hasAbility ?shieldAbility, ?controlAbility .
  ?shieldAbility lol:hasEffect ?shieldEffect .
  ?shieldEffect lol:hasMechanic lol:Shield ;
                lol:hasTargetType lol:Ally ;
                lol:conditionText ?shieldCondition .
  ?controlAbility lol:hasEffect ?controlEffect .
  ?controlEffect lol:hasMechanic ?controlMechanic ;
                 lol:hasTargetType lol:Enemy ;
                 lol:conditionText ?controlCondition .
  ?controlMechanic a lol:MovementControlMechanic .
}
ORDER BY ?champion ?shieldAbility ?controlAbility ?controlMechanic
```

**Ожидаемый результат на `lol_full.owl`** — 7 строк.

| `?champion` | `?name` | `?shieldAbility` | `?shieldCondition` | `?controlAbility` | `?controlMechanic` | `?controlCondition` |
| --- | --- | --- | --- | --- | --- | --- |
| Karma | Карма | Karma_E | Выбранный союзник; при усилении Мантрой эффект распространяется на ближайших союзных чемпионов. | Karma_Q | Slow | Попадание сгустком энергии; замедление целей, указанных в tooltip. |
| Karma | Карма | Karma_E | Выбранный союзник; при усилении Мантрой эффект распространяется на ближайших союзных чемпионов. | Karma_W | Root | Связь должна сохраниться до конца задержки; для усиленной версии длительность увеличивается. |
| Lux | Люкс | Lux_W | Жезл должен коснуться союзника на пути вперед или обратно. | Lux_E | Slow | Противник находится в области аномалии; tooltip также описывает краткое замедление после взрыва. |
| Lux | Люкс | Lux_W | Жезл должен коснуться союзника на пути вперед или обратно. | Lux_Q | Root | Сфера должна попасть в цель; обездвиживаются первые два врага на пути. |
| Morgana | Моргана | Morgana_E | Щит на выбранном союзном чемпионе поглощает магический урон; это не универсальный щит от любого урона. | Morgana_Q | Root | Первый враг, в которого попал снаряд. |
| Morgana | Моргана | Morgana_E | Щит на выбранном союзном чемпионе поглощает магический урон; это не универсальный щит от любого урона. | Morgana_R | Slow | Вражеский чемпион связан цепью Моргани. |
| Morgana | Моргана | Morgana_E | Щит на выбранном союзном чемпионе поглощает магический урон; это не универсальный щит от любого урона. | Morgana_R | Stun | Цепь с вражеским чемпионом должна сохраниться до окончания задержки. |

## 2. Основные умения Люкс

У Люкс пассивное умение P «Иллюминация». Активные умения — Q «Сковывание света», W «Призматический барьер», E «Светящаяся сингулярность» и R «Последняя искра».

```sparql
PREFIX lol: <https://example.org/lol-ontology#>

SELECT ?slot ?ability ?abilityName ?kind
WHERE {
  VALUES (?slot ?position) { ("P" 0) ("Q" 1) ("W" 2) ("E" 3) ("R" 4) }
  VALUES ?kind { lol:PassiveAbility lol:ActiveAbility }
  ?ability a ?kind ;
           lol:isAbilityOf lol:Lux ;
           lol:slot ?slot ;
           lol:name ?abilityName .
}
ORDER BY ?position ?ability
```

**Ожидаемый результат на `lol_full_inferred.owl`** — 5 строк.

| `?slot` | `?ability` | `?abilityName` | `?kind` |
| --- | --- | --- | --- |
| P | Lux_P | Иллюминация | PassiveAbility |
| Q | Lux_Q | Сковывание света | ActiveAbility |
| W | Lux_W | Призматический барьер | ActiveAbility |
| E | Lux_E | Светящаяся сингулярность | ActiveAbility |
| R | Lux_R | Последняя искра | ActiveAbility |

## 3. Получатели лечения

Карма восстанавливает себе здоровье умением W «Решимость» при усилении Мантрой. Моргана восстанавливает себе здоровье пассивным умением P «Вытягивание души» при нанесении урона чемпионам, большим миньонам или средним и большим лесным монстрам. В разметке нет эффектов лечения с целью Ally.

```sparql
PREFIX lol: <https://example.org/lol-ontology#>

SELECT ?champion ?championName ?ability ?slot ?abilityName ?effect ?target ?condition
WHERE {
  VALUES ?target { lol:Self lol:Ally }
  ?champion a lol:Champion ;
            lol:name ?championName ;
            lol:hasAbility ?ability .
  ?ability lol:slot ?slot ;
           lol:name ?abilityName ;
           lol:hasEffect ?effect .
  ?effect lol:hasMechanic lol:Heal ;
          lol:hasTargetType ?target ;
          lol:conditionText ?condition .
}
ORDER BY ?champion ?slot ?target ?effect
```

**Ожидаемый результат на `lol_full.owl`** — 2 строки.

| `?champion` | `?championName` | `?ability` | `?slot` | `?abilityName` | `?effect` | `?target` | `?condition` |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Karma | Карма | Karma_W | W | Решимость | Karma_W_Heal_Self | Self | Только усиление Мантрой; Карма восстанавливает собственное здоровье. |
| Morgana | Моргана | Morgana_P | P | Вытягивание души | Morgana_P_Heal_Self | Self | Моргана наносит урон чемпионам, большим миньонам, средним или большим лесным монстрам. |

## 4. Защита союзника от контроля

Моргана защищает союзника умением E «Черный щит», пока барьер не уничтожен. Защита подтверждается описанием умения в записи о Моргане из Data Dragon 16.20.1 / ru_RU.

```sparql
PREFIX lol: <https://example.org/lol-ontology#>

SELECT ?champion ?championName ?ability ?slot ?abilityName ?effect
       ?condition ?evidenceField ?evidence ?source
WHERE {
  ?champion a lol:Champion ;
            lol:name ?championName ;
            lol:hasAbility ?ability .
  ?ability lol:slot ?slot ;
           lol:name ?abilityName ;
           lol:hasEffect ?effect .
  ?effect lol:hasMechanic lol:ControlImmunity ;
          lol:hasTargetType lol:Ally ;
          lol:conditionText ?condition ;
          lol:evidenceField ?evidenceField ;
          lol:evidenceText ?evidence ;
          lol:hasSource/lol:sourceURL ?source .
}
ORDER BY ?champion ?ability ?effect ?source
```

**Ожидаемый результат на `lol_full.owl`** — 1 строка.

| Переменная | Значение |
| --- | --- |
| `?champion` | Morgana |
| `?championName` | Моргана |
| `?ability` | Morgana_E |
| `?slot` | E |
| `?abilityName` | Черный щит |
| `?effect` | Morgana_E_ControlImmunity_Ally |
| `?condition` | Барьер блокирует описанные эффекты контроля, пока не будет уничтожен. |
| `?evidenceField` | description_text |
| `?evidence` | Моргана защищает союзника защитным барьером из звездного огня, который поглощает магический урон и эффекты контроля, пока не будет уничтожен. |
| `?source` | https://ddragon.leagueoflegends.com/cdn/16.20.1/data/ru_RU/champion/Morgana.json |

## 5. Максимальная базовая скорость среди Mage и Support

Максимальная базовая скорость равна 340. Её имеют Брэнд, Хеймердингер, Нико, Вел'Коз, Зерат и Зайра.

```sparql
PREFIX lol: <https://example.org/lol-ontology#>

SELECT ?champion ?name ?speed
WHERE {
  {
    SELECT (MAX(?candidateSpeed) AS ?maxSpeed)
    WHERE {
      ?candidate a lol:Champion ;
                 lol:hasCategory lol:Category_Mage, lol:Category_Support ;
                 lol:baseMoveSpeed ?candidateSpeed .
    }
  }
  ?champion a lol:Champion ;
            lol:hasCategory lol:Category_Mage, lol:Category_Support ;
            lol:name ?name ;
            lol:baseMoveSpeed ?speed .
  FILTER (?speed = ?maxSpeed)
}
ORDER BY ?champion
```

**Ожидаемый результат на `lol_full.owl`** — 6 строк.

| `?champion` | `?name` | `?speed` |
| --- | --- | --- |
| Brand | Брэнд | 340.0 |
| Heimerdinger | Хеймердингер | 340.0 |
| Neeko | Нико | 340.0 |
| Velkoz | Вел'Коз | 340.0 |
| Xerath | Зерат | 340.0 |
| Zyra | Зайра | 340.0 |

## 6. Механики умений Кармы

Девять размеченных механик Кармы — сокращение перезарядки, урон, усиление умения, лечение, ускорение, раскрытие цели, обездвиживание, щит и замедление.

```sparql
PREFIX lol: <https://example.org/lol-ontology#>

SELECT ?mechanic ?mechanicName
WHERE {
  lol:Karma lol:canApplyMechanic ?mechanic .
  ?mechanic lol:name ?mechanicName .
}
ORDER BY ?mechanic
```

**Ожидаемый результат на `lol_full_inferred.owl`** — 9 строк.

| `?mechanic` | `?mechanicName` |
| --- | --- |
| CooldownReduction | Сокращение перезарядки |
| Damage | Урон |
| Empower | Усиление умения |
| Heal | Лечение |
| MovementSpeedBoost | Ускорение |
| Reveal | Раскрытие цели |
| Root | Обездвиживание |
| Shield | Щит |
| Slow | Замедление |

## 7. Умения с эффектами для самого чемпиона и противника

Карма с помощью W может нанести урон, раскрыть и обездвижить противника, а при усилении Мантрой — восстановить себе здоровье. Моргана с помощью R ускоряет себя и может нанести урон, замедлить и оглушить противника.

```sparql
PREFIX lol: <https://example.org/lol-ontology#>

SELECT DISTINCT ?champion ?ability ?selfMechanic ?enemyMechanic
WHERE {
  ?champion a lol:Champion ;
            lol:hasAbility ?ability .
  ?selfEffect lol:effectOf ?ability ;
              lol:hasTargetType lol:Self ;
              lol:hasMechanic ?selfMechanic .
  ?enemyEffect lol:effectOf ?ability ;
               lol:hasTargetType lol:Enemy ;
               lol:hasMechanic ?enemyMechanic .
}
ORDER BY ?champion ?ability ?selfMechanic ?enemyMechanic
```

**Ожидаемый результат на `lol_full_inferred.owl`** — 6 строк.

| `?champion` | `?ability` | `?selfMechanic` | `?enemyMechanic` |
| --- | --- | --- | --- |
| Karma | Karma_W | Heal | Damage |
| Karma | Karma_W | Heal | Reveal |
| Karma | Karma_W | Heal | Root |
| Morgana | Morgana_R | MovementSpeedBoost | Damage |
| Morgana | Morgana_R | MovementSpeedBoost | Slow |
| Morgana | Morgana_R | MovementSpeedBoost | Stun |

## 8. Категории чемпионов, использующих энергию

В категории Assassin четыре чемпиона с энергией, в Fighter — два, в Mage и Tank — по одному. Чемпион с двумя категориями учитывается в обеих.

```sparql
PREFIX lol: <https://example.org/lol-ontology#>

SELECT ?category (COUNT(DISTINCT ?champion) AS ?championCount)
WHERE {
  ?champion a lol:Champion ;
            lol:resourceType ?resource ;
            lol:hasCategory ?category .
  FILTER (STR(?resource) = "Энергия")
}
GROUP BY ?category
ORDER BY DESC(?championCount) ?category
```

**Ожидаемый результат на `lol_full.owl`** — 4 строки.

| `?category` | `?championCount` |
| --- | --- |
| Category_Assassin | 4 |
| Category_Fighter | 2 |
| Category_Mage | 1 |
| Category_Tank | 1 |
