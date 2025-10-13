using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace class3
{
    public class BattleManager
    {
        private readonly List<Legend> _legends = new();
        private readonly Random _random = new Random();

        public BattleManager(int legendCount)
        {
            if (legendCount <= 0)
                throw new ArgumentException("Legend count must be greater than zero.", nameof(legendCount));

            for (int i = 0; i < legendCount; i++)
            {
                _legends.Add(new Garen());
                _legends.Add(new Mantis());
            }
        }

        public void StartFight()
        {
            Console.WriteLine("\n=== Battle Start! ===\n");
            int round = 1;

            while (GetAliveLegends().Count() > 1)
            {
                Console.WriteLine($"\n--- Round {round} ---");

                var aliveLegends = GetAliveLegends().ToList();
                var attacker = aliveLegends[_random.Next(aliveLegends.Count)];
                var possibleTargets = aliveLegends.Where(l => l != attacker).ToList();

                if (possibleTargets.Any())
                {
                    var target = possibleTargets[_random.Next(possibleTargets.Count)];
                    attacker.Attack(target);

                  
                    if (_random.Next(100) < 20 && attacker.IsAlive)
                    {
                        attacker.ApplySpecialAbility(possibleTargets.ToArray());
                    }
                }

                round++;
           
            }

            AnnounceWinner();
        }

        private IEnumerable<Legend> GetAliveLegends()
        {
            return _legends.Where(l => l.IsAlive);
        }

        private void AnnounceWinner()
        {
            Console.WriteLine("\n=== Battle End! ===\n");

            var winner = GetAliveLegends().FirstOrDefault();
            if (winner != null)
            {
                Console.WriteLine($"{winner.Name} is the WINNER with {winner.HP} HP remaining!");
            }
            else
            {
                Console.WriteLine("All legends have fallen! It's a draw!");
            }
        }
    }
}