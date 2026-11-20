# Ответы, SPARQL-запросы и ожидаемые результаты

Граф охватывает Data Dragon 16.20.1 / ru_RU: 173 чемпиона и 865 основных умений. Эффекты вручную классифицированы для Кармы, Люкс и Морганы. Цель Ally или Enemy обозначает тип цели эффекта, а не конкретного игрока в матче. lol_full.owl содержит исходные утверждения, lol_full_inferred.owl — факты, выведенные HermiT.

## 1. Щит союзнику и контроль передвижения

**Вопрос.** Какие чемпионы категории Mage имеют по меньшей мере одно основное умение с эффектом щита для Ally и другое основное умение с эффектом контроля передвижения Enemy?

В онтологии представлены категории целей Ally и Enemy, но не конкретные персонажи матча и отношения между ними. По записанным эффектам подходят три чемпиона: Карма, Люкс и Моргана. Запрос возвращает семь сочетаний умений со щитом и умений контроля.

```sparql
PREFIX lol: <https://example.org/lol-ontology#>

SELECT DISTINCT ?champion ?name ?shieldAbility ?controlAbility ?controlMechanic
WHERE {
  ?champion a lol:Champion ; lol:name ?name ;
            lol:hasCategory lol:Category_Mage ;
            lol:hasAbility ?shieldAbility, ?controlAbility .
  ?shieldAbility lol:hasEffect ?shieldEffect .
  ?shieldEffect lol:hasMechanic lol:Shield ;
                lol:hasTargetType lol:Ally .
  ?controlAbility lol:hasEffect ?controlEffect .
  ?controlEffect lol:hasMechanic ?controlMechanic ;
                 lol:hasTargetType lol:Enemy .
  ?controlMechanic a lol:MovementControlMechanic .
}
ORDER BY ?champion ?shieldAbility ?controlAbility ?controlMechanic
```

**Ожидаемый результат на lol_full.owl** — 7 строк.

| champion | name | shieldAbility | controlAbility | controlMechanic |
| --- | --- | --- | --- | --- |
| Karma | Карма | Karma_E | Karma_Q | Slow |
| Karma | Карма | Karma_E | Karma_W | Root |
| Lux | Люкс | Lux_W | Lux_E | Slow |
| Lux | Люкс | Lux_W | Lux_Q | Root |
| Morgana | Моргана | Morgana_E | Morgana_Q | Root |
| Morgana | Моргана | Morgana_E | Morgana_R | Slow |
| Morgana | Моргана | Morgana_E | Morgana_R | Stun |

## 2. Пассивное умение Люкс

**Вопрос.** В каком слоте находится пассивное умение, принадлежащее Люкс?

Пассивное умение Люкс — P «Иллюминация».

```sparql
PREFIX lol: <https://example.org/lol-ontology#>

SELECT ?slot ?ability ?abilityName
WHERE {
  ?ability a lol:PassiveAbility ;
           lol:isAbilityOf lol:Lux ;
           lol:slot ?slot ;
           lol:name ?abilityName .
}
```

**Ожидаемый результат на lol_full_inferred.owl** — 1 строка.

| slot | ability | abilityName |
| --- | --- | --- |
| P | Lux_P | Иллюминация |

## 3. Условия и получатели эффектов лечения

**Вопрос.** Какие условия указаны для размеченных эффектов лечения с учётом того, кто является целью каждого эффекта?

У Кармы умение W «Решимость» восстанавливает здоровье самой Кармы при усилении Мантрой. Пассивное умение Морганы «Вытягивание души» лечит её при нанесении урона чемпионам, большим миньонам либо средним и большим лесным монстрам. Оба размеченных эффекта направлены на самого чемпиона.

```sparql
PREFIX lol: <https://example.org/lol-ontology#>

SELECT ?champion ?championName ?ability ?slot ?abilityName ?target ?condition
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
ORDER BY ?champion ?slot ?target
```

**Ожидаемый результат на lol_full.owl** — 2 строк.

| champion | championName | ability | slot | abilityName | target | condition |
| --- | --- | --- | --- | --- | --- | --- |
| Karma | Карма | Karma_W | W | Решимость | Self | Только усиление Мантрой; Карма восстанавливает собственное здоровье. |
| Morgana | Моргана | Morgana_P | P | Вытягивание души | Self | Моргана наносит урон чемпионам, большим миньонам, средним или большим лесным монстрам. |

## 4. Защита союзника от контроля

**Вопрос.** Какое размеченное умение защищает союзника от эффектов контроля, при каком условии действует защита и каким источником она подтверждена?

Моргана защищает союзника умением E «Черный щит», пока барьер не уничтожен. Защита подтверждается описанием умения в записи о Моргане из Data Dragon 16.20.1 / ru_RU.

```sparql
PREFIX lol: <https://example.org/lol-ontology#>

SELECT ?champion ?championName ?ability ?slot ?abilityName ?condition ?evidenceField ?evidence ?source
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
ORDER BY ?champion ?ability ?source
```

**Ожидаемый результат на lol_full.owl** — 1 строка.

| champion | championName | ability | slot | abilityName | condition | evidenceField | evidence | source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Morgana | Моргана | Morgana_E | E | Черный щит | Барьер блокирует описанные эффекты контроля, пока не будет уничтожен. | description_text | Моргана защищает союзника защитным барьером из звездного огня, который поглощает магический урон и эффекты контроля, пока не будет уничтожен. | https://ddragon.leagueoflegends.com/cdn/16.20.1/data/ru_RU/champion/Morgana.json |

## 5. Максимальная базовая скорость среди Mage и Support

**Вопрос.** Кто имеет наибольшую базовую скорость передвижения среди чемпионов, одновременно относящихся к категориям Mage и Support?

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

**Ожидаемый результат на lol_full.owl** — 6 строк.

| champion | name | speed |
| --- | --- | --- |
| Brand | Брэнд | 340.0 |
| Heimerdinger | Хеймердингер | 340.0 |
| Neeko | Нико | 340.0 |
| Velkoz | Вел'Коз | 340.0 |
| Xerath | Зерат | 340.0 |
| Zyra | Зайра | 340.0 |

## 6. Механика, цель и условие эффектов умений Кармы

**Вопрос.** Какие механики, цели и условия применения указаны для каждого размеченного эффекта основных умений Кармы?

В онтологии размеченный эффект — это запись об эффекте конкретного умения, вручную классифицированная по механике и цели, с текстом условия и ссылкой на источник. Для пяти основных умений Кармы указано десять таких эффектов. Запрос перечисляет умение, механику, цель и условие каждого эффекта.

```sparql
PREFIX lol: <https://example.org/lol-ontology#>

SELECT ?slot ?abilityName ?effect ?mechanicName ?targetName ?condition
WHERE {
  lol:Karma a lol:Champion ;
            lol:hasAbility ?ability .
  ?ability lol:slot ?slot ;
           lol:name ?abilityName ;
           lol:hasEffect ?effect .
  ?effect lol:hasMechanic ?mechanic ;
          lol:hasTargetType ?target ;
          lol:conditionText ?condition .
  ?mechanic lol:name ?mechanicName .
  ?target lol:name ?targetName .
}
ORDER BY ?slot ?effect
```

**Ожидаемый результат на lol_full.owl** — 10 строк.

| slot | abilityName | effect | mechanicName | targetName | condition |
| --- | --- | --- | --- | --- | --- |
| E | Воодушевление | Karma_E_MovementSpeedBoost_Ally | Ускорение | Союзник | Союзник получает Воодушевление; усиление Мантрой распространяет эффект на ближайших союзников. |
| E | Воодушевление | Karma_E_Shield_Ally | Щит | Союзник | Выбранный союзник; при усилении Мантрой эффект распространяется на ближайших союзных чемпионов. |
| P | Разгорающийся огонь | Karma_P_CooldownReduction_OwnAbility | Сокращение перезарядки | Собственное умение | При нанесении урона умениями; сокращается перезарядка Мантры. |
| Q | Внутреннее пламя | Karma_Q_Damage_Enemy | Урон | Противник | Попадание сгустком энергии; урон получает первая цель и окружающие враги. |
| Q | Внутреннее пламя | Karma_Q_Slow_Enemy | Замедление | Противник | Попадание сгустком энергии; замедление целей, указанных в tooltip. |
| R | Мантра | Karma_R_Empower_OwnAbility | Усиление умения | Собственное умение | Усиливает следующее умение Кармы, примененное в течение 8 секунд. |
| W | Решимость | Karma_W_Damage_Enemy | Урон | Противник | Выбранная вражеская цель связана с Кармой; повторный урон, если связь сохраняется. |
| W | Решимость | Karma_W_Heal_Self | Лечение | Сам чемпион | Только усиление Мантрой; Карма восстанавливает собственное здоровье. |
| W | Решимость | Karma_W_Reveal_Enemy | Раскрытие цели | Противник | На время связи раскрывается выбранная вражеская цель. |
| W | Решимость | Karma_W_Root_Enemy | Обездвиживание | Противник | Связь должна сохраниться до конца задержки; для усиленной версии длительность увеличивается. |

## 7. Умения с эффектами для самого чемпиона и противника

**Вопрос.** Какие умения одного чемпиона имеют эффекты и для него самого, и для противника, и какие механики указаны для этих целей?

У Кармы умение W может нанести противнику урон, раскрыть его и обездвижить, а при усилении Мантрой восстановить здоровье самой Кармы. У Морганы умение R ускоряет саму Моргану и может нанести противнику урон, замедлить и оглушить его.

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

**Ожидаемый результат на lol_full_inferred.owl** — 6 строк.

| champion | ability | selfMechanic | enemyMechanic |
| --- | --- | --- | --- |
| Karma | Karma_W | Heal | Damage |
| Karma | Karma_W | Heal | Reveal |
| Karma | Karma_W | Heal | Root |
| Morgana | Morgana_R | MovementSpeedBoost | Damage |
| Morgana | Morgana_R | MovementSpeedBoost | Slow |
| Morgana | Morgana_R | MovementSpeedBoost | Stun |

## 8. Чемпионы с энергией по категориям

**Вопрос.** Сколько чемпионов с игровым ресурсом «Энергия» относится к каждой категории?

В категории Assassin четыре чемпиона с энергией, в Fighter — два, в Mage и Tank — по одному. Учитываются только экземпляры класса Champion. Чемпион с двумя категориями входит в подсчёт каждой из них.

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

**Ожидаемый результат на lol_full.owl** — 4 строк.

| category | championCount |
| --- | --- |
| Category_Assassin | 4 |
| Category_Fighter | 2 |
| Category_Mage | 1 |
| Category_Tank | 1 |

