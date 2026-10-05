using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace class8.Core;

[AttributeUsage(AttributeTargets.Method, Inherited = false, AllowMultiple = false)]
public class CombatSkillAttribute : Attribute
{
    public string Name { get; }
    public TriggerType Trigger { get; }
    public int Priority { get; }

    public CombatSkillAttribute(string name, TriggerType trigger, int priority = 1)
    {
        Name = name;
        Trigger = trigger;
        Priority = priority;
    }
}
