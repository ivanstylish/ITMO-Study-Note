using class8.Core;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;

namespace class8.Core;

// Контекст исполнения: данные, доступные внутри навыка
public class BattleContext
{
    public int DamageDealt { get; set; }
    public UnitStats Attacker { get; set; }
    public UnitStats Defender { get; set; }
}