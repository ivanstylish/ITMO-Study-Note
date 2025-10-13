using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace class3
{
    public class Garen : Legend
    {
        public Garen() : base("Garen", 300, 50, 70, "HeavyBlow")
        {
        }

        public override void ApplySpecialAbility(params Legend[] targets)
        {
            Console.WriteLine($"{Name} uses {Skill}!");
            foreach (var target in targets)
            {
                if (target != this && target.IsAlive)
                {
                    int bonusDamage = AttackPower / 2;
                    target.TakeDamage(bonusDamage);
                    Console.WriteLine($"{Name}'s Heavy Blow deals {bonusDamage} bonus damage to {target.Name}!");
                }
            }
        }
    }
}
