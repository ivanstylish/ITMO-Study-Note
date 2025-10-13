using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace class3
{
    static class Program
    {
        public static void Main(string[] args)
        {
            Console.WriteLine("=== Legend Battle Simulator ===\n");

            var templates = GetLegendTemplates();
            Console.WriteLine("Available Legends:");
            foreach (var legend in templates)
            {
                Console.WriteLine($"  {legend.GetType().Name} - HP: {legend.HP}, Attack: {legend.AttackPower}, Defense: {legend.Defense}, Skill: {legend.Skill}");
            }

            Console.WriteLine("\nStarting battle with 2 pairs of legends...\n");

            var battleManager = new BattleManager(2);
            battleManager.StartFight();

            Console.WriteLine("\nPress any key to exit...");
            Console.ReadKey();
        }

        private static IEnumerable<Legend> GetLegendTemplates()
        {
            return new List<Legend>
            {
                new Garen(),
                new Mantis()
            };
        }
    }
}