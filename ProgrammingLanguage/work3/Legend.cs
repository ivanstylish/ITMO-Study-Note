using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection.Metadata.Ecma335;
using System.Text;
using System.Threading.Tasks;

namespace class3
{
    public abstract class Legend
    {
        private static readonly Random _random = new Random(); // 使用静态Random避免重复

        public Legend(string legendName, int hp, int attackPower, int defense, string skill)
        {
            if (string.IsNullOrWhiteSpace(legendName))
                throw new ArgumentNullException(nameof(legendName), "Name can't be null or empty.");

            Name = $"{legendName} #{_random.Next(0, 1000)}";
            HP = hp;
            AttackPower = attackPower;
            Defense = defense;
            Skill = skill;
        }

        public string Name { get; set; }
        public int HP { get; set; }
        public int AttackPower { get; set; }
        public int Defense { get; set; }
        public string Skill { get; set; }
        public bool IsAlive => HP > 0;

        public void Attack(Legend target)
        {
            if (target == null || !target.IsAlive)
                return;

            int damage = Math.Max(0, AttackPower - target.Defense);
            target.TakeDamage(damage);
            Console.WriteLine($"{Name} attacks {target.Name} for {damage} damage!");
        }

        public void TakeDamage(int damage)
        {
            HP -= damage;

            if (this is Garen)
                Console.Beep(800, 200);
            else if (this is Mantis)
                Console.Beep(200, 50);

            if (HP < 0)
                HP = 0;

            Console.WriteLine($"{Name} takes {damage} damage! Remaining HP: {HP}");

            if (!IsAlive)
                Console.WriteLine($"{Name} has been defeated!");
        }

        public void Heal(int amount)
        {
            if (amount < 0)
                throw new ArgumentException("Heal amount cannot be negative.", nameof(amount));

            HP += amount;
            Console.WriteLine($"{Name} is healed by {amount}. Current HP: {HP}");
        }

        public abstract void ApplySpecialAbility(params Legend[] targets);
    }
}
