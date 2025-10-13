using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace class3
{
    public class Mantis : Legend
    {
        private static readonly Random _random = new Random();
        public Mantis() : base("Mantis", 200, 80, 40, "Invisible") 
        {
        }
        public override void ApplySpecialAbility(params Legend[] targets)
        {
            int invisiTime = _random.Next(3, 6);
            int healAmount = _random.Next(20, 31);

            Console.WriteLine($"{Name} uses {Skill}! Becomes invisible for {invisiTime}s");

            // 闪避一次攻击
            int dodgedDamage = Defense / 2;
            Console.WriteLine($"{Name} dodges {dodgedDamage} damage while invisible!");

            // 治疗自己
            Heal(healAmount);
        }
    }
}