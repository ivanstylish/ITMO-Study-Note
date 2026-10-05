using class8;
using class8.Core;
using System.Reflection;

class Program
{
    static void Main()
    {
        var engine = new SkillEngine();

        engine.RegisterAssembly(Assembly.GetExecutingAssembly());

    
        var context = new BattleContext
        {
            DamageDealt = 100,
            Attacker = new UnitStats { Hp = 50 },
            Defender = new UnitStats { Hp = 100 }
        };

        Console.WriteLine("--- Starting Attack Phase ---");

        
        engine.ExecutePipeline(TriggerType.OnAttack, context);

        Console.WriteLine($"Attacker Final HP: {context.Attacker.Hp}");
    }
}