using class4;
using OpenXmlPowerTools;
using System.Runtime.InteropServices;

namespace class4
{
    public static class Program
    {
        public static void Main()
        {

            var currentDirectory = System.IO.Directory.GetCurrentDirectory();
            var filePath = System.IO.Directory.GetFiles(currentDirectory, "*.csv").First();

            IReadOnlyList<MovieCredit> movieCredits = null;
            try
            {
                var parser = new MovieCreditsParser(filePath);
                movieCredits = parser.Parse();
            }
            catch (Exception exc)
            {
                Console.WriteLine("Не удалось распарсить csv");
                Environment.Exit(1);
            }


            Console.WriteLine("1. Фильмы, снятые режиссером Steven Spielberg:");
            var spielbergMovies = movieCredits
                .Where(movie => movie.Crew.Any(crew =>
                    crew.Name == "Steven Spielberg" && crew.Job == "Director"))
                .Select(movie => movie.Title);
            Console.WriteLine(string.Join(Environment.NewLine, spielbergMovies));
            Console.WriteLine();


            Console.WriteLine("2. Все персонажи, которых сыграл Tom Hanks:");
            var tomHanksRoles = movieCredits
                .SelectMany(movie => movie.Cast)
                .Where(cast => cast.Name == "Tom Hanks")
                .Select(cast => $"{cast.Character} (фильм: {GetMovieTitle(movieCredits, cast)})")
                .Distinct();
            Console.WriteLine(string.Join(Environment.NewLine, tomHanksRoles));
            Console.WriteLine();


            Console.WriteLine("3. 5 фильмов с самым большим количеством актеров:");
            var top5MoviesWithMostActors = movieCredits
                .Select(movie => new
                {
                    MovieTitle = movie.Title,
                    ActorCount = movie.Cast.Count
                })
                .OrderByDescending(movie => movie.ActorCount)
                .Take(5);
            Console.WriteLine(string.Join(Environment.NewLine,
                top5MoviesWithMostActors.Select(m => $"{m.MovieTitle} - {m.ActorCount} актеров")));
            Console.WriteLine();


            Console.WriteLine("4. Топ-10 самых востребованных актеров:");
            var top10Actors = movieCredits
                .SelectMany(movie => movie.Cast)
                .GroupBy(cast => cast.Name)
                .Select(group => new
                {
                    ActorName = group.Key,
                    MovieCount = group.Count()
                })
                .OrderByDescending(actor => actor.MovieCount)
                .Take(10);
            Console.WriteLine(string.Join(Environment.NewLine,
                top10Actors.Select(a => $"{a.ActorName} - {a.MovieCount} фильмов")));
            Console.WriteLine();


            Console.WriteLine("5. Все уникальные департаменты съемочной группы:");
            var uniqueDepartments = movieCredits
                .SelectMany(movie => movie.Crew)
                .Select(crew => crew.Department)
                .Distinct()
                .OrderBy(dept => dept);
            Console.WriteLine(string.Join(Environment.NewLine, uniqueDepartments));
            Console.WriteLine();


            Console.WriteLine("6. Фильмы, где Hans Zimmer был композитором:");
            var hansZimmerMovies = movieCredits
                .Where(movie => movie.Crew.Any(crew =>
                    crew.Name == "Hans Zimmer" && crew.Job == "Original Music Composer"))
                .Select(movie => movie.Title);
            Console.WriteLine(string.Join(Environment.NewLine, hansZimmerMovies));
            Console.WriteLine();

            Console.WriteLine("7. Словарь ID фильма -> режиссер (первые 10):");
            var directorDict = movieCredits
                .SelectMany(movie => movie.Crew
                    .Where(crew => crew.Job == "Director")
                    .Select(crew => new { movie.MovieId, Director = crew.Name }))
                .GroupBy(x => x.MovieId)
                .ToDictionary(g => g.Key, g => string.Join(", ", g.Select(x => x.Director)));


            foreach (var item in directorDict.Take(10))
            {
                Console.WriteLine($"ID фильма {item.Key}: {item.Value}");
            }
            Console.WriteLine();


            Console.WriteLine("8. Фильмы с Brad Pitt и George Clooney:");
            var bradAndGeorgeMovies = movieCredits
                .Where(movie =>
                    movie.Cast.Any(cast => cast.Name == "Brad Pitt") &&
                    movie.Cast.Any(cast => cast.Name == "George Clooney"))
                .Select(movie => movie.Title);
            Console.WriteLine(string.Join(Environment.NewLine, bradAndGeorgeMovies));
            Console.WriteLine();


            Console.WriteLine("9. Общее количество людей в департаменте Camera:");
            var cameraDepartmentCount = movieCredits
                .SelectMany(movie => movie.Crew)
                .Count(crew => crew.Department == "Camera");
            Console.WriteLine($"В департаменте Camera работает {cameraDepartmentCount} человек");
            Console.WriteLine();


            Console.WriteLine("10. Люди в фильме Titanic, бывшие и актерами и членами съемочной группы:");
            var titanic = movieCredits.FirstOrDefault(m => m.Title.Contains("Titanic"));
            if (titanic != null)
            {
                var actorIds = titanic.Cast.Select(c => c.Id).ToHashSet();
                var crewIds = titanic.Crew.Select(c => c.Id).ToHashSet();
                var intersectionIds = actorIds.Intersect(crewIds);


                var actorNames = titanic.Cast
                    .Where(c => intersectionIds.Contains(c.Id))
                    .Select(c => c.Name);

                var crewNames = titanic.Crew
                    .Where(c => intersectionIds.Contains(c.Id))
                    .Select(c => c.Name);

                var people = actorNames.Concat(crewNames).Distinct();

                Console.WriteLine(string.Join(Environment.NewLine, people));
            }
            Console.WriteLine();


            Console.WriteLine("11. Внутренний круг режиссера Quentin Tarantino - топ-5 съемочной группы:");
            var tarantinoCrew = movieCredits
                .Where(movie => movie.Crew.Any(crew =>
                    crew.Name == "Quentin Tarantino" && crew.Job == "Director"))
                .SelectMany(movie => movie.Crew)
                .Where(crew => crew.Name != "Quentin Tarantino")
                .GroupBy(crew => crew.Name)
                .Select(group => new
                {
                    Name = group.Key,
                    CollaborationCount = group.Count()
                })
                .OrderByDescending(x => x.CollaborationCount)
                .Take(5);
            Console.WriteLine(string.Join(Environment.NewLine,
                tarantinoCrew.Select(x => $"{x.Name} - {x.CollaborationCount} сотрудничеств")));
            Console.WriteLine();

         
            Console.WriteLine("12. Топ-10 пар актеров, чаще всего снимавшихся вместе:");
            var actorPairs = movieCredits
                .SelectMany(movie =>
                    from actor1 in movie.Cast
                    from actor2 in movie.Cast
                    where actor1.Id < actor2.Id
                    select new { Actor1 = actor1.Name, Actor2 = actor2.Name })
                .GroupBy(pair => new { pair.Actor1, pair.Actor2 })
                .Select(group => new
                {
                    Pair = group.Key,
                    Count = group.Count()
                })
                .OrderByDescending(x => x.Count)
                .Take(10);

            foreach (var pair in actorPairs)
            {
                Console.WriteLine($"{pair.Pair.Actor1} & {pair.Pair.Actor2} - {pair.Count} совместных фильмов");
            }
            Console.WriteLine();


            Console.WriteLine("13. Топ-5 членов съемочной группы с наибольшим разнообразием департаментов:");
            var versatileCrew = movieCredits
                .SelectMany(movie => movie.Crew)
                .GroupBy(crew => crew.Name)
                .Select(group => new
                {
                    Name = group.Key,
                    DepartmentCount = group.Select(c => c.Department).Distinct().Count()
                })
                .OrderByDescending(x => x.DepartmentCount)
                .Take(5);
            Console.WriteLine(string.Join(Environment.NewLine,
                versatileCrew.Select(x => $"{x.Name} - {x.DepartmentCount} департаментов")));
            Console.WriteLine();


            Console.WriteLine("14. Фильмы, где один человек был режиссером, сценаристом и продюсером:");
            var tripleThreatMovies = movieCredits
                .Where(movie =>
                {
                    var crewGroups = movie.Crew
                        .Where(c => c.Job == "Director" || c.Job == "Writer" || c.Job == "Producer")
                        .GroupBy(c => c.Id)
                        .Where(g => g.Select(c => c.Job).Distinct().Count() >= 3);
                    return crewGroups.Any();
                })
                .Select(movie => new
                {
                    Title = movie.Title,
                    People = movie.Crew
                        .Where(c => c.Job == "Director" || c.Job == "Writer" || c.Job == "Producer")
                        .GroupBy(c => c.Id)
                        .Where(g => g.Select(c => c.Job).Distinct().Count() >= 3)
                        .Select(g => g.First().Name) 
                });

            foreach (var movie in tripleThreatMovies)
            {
                Console.WriteLine($"{movie.Title}: {string.Join(", ", movie.People)}");
            }
            Console.WriteLine();


            Console.WriteLine("15. Актеры на расстоянии двух шагов от Kevin Bacon:");
            var kevinBaconSeparations = FindKevinBaconSeparations(movieCredits, 2);
            Console.WriteLine($"Найдено {kevinBaconSeparations.Count} актеров на расстоянии двух шагов от Kevin Bacon");

            foreach (var actor in kevinBaconSeparations.Take(20))
            {
                Console.WriteLine(actor);
            }
            Console.WriteLine("...");
            Console.WriteLine();

            Console.WriteLine("16. Средний размер актерского состава и съемочной группы по режиссерам:");
            var directorStats = movieCredits
                .SelectMany(movie => movie.Crew
                    .Where(crew => crew.Job == "Director")
                    .Select(crew => new { Director = crew.Name, Movie = movie }))
                .GroupBy(x => x.Director)
                .Select(g => new
                {
                    Director = g.Key,
                    AvgCastSize = g.Average(x => x.Movie.Cast.Count),
                    AvgCrewSize = g.Average(x => x.Movie.Crew.Count),
                    MovieCount = g.Count()
                })
                .OrderByDescending(x => x.MovieCount)
                .Take(10);

            foreach (var stat in directorStats)
            {
                Console.WriteLine($"{stat.Director}: {stat.MovieCount} фильмов, " +
                                 $"в среднем {stat.AvgCastSize:F1} актеров, " +
                                 $"в среднем {stat.AvgCrewSize:F1} членов съемочной группы");
            }
            Console.WriteLine();


            Console.WriteLine("17. Универсалы: актеры, также работавшие в съемочной группе:");
            var actorCrewPeople = FindActorCrewPeople(movieCredits);

            foreach (var person in actorCrewPeople.Take(10))
            {
                Console.WriteLine($"{person.Item1}: основной департамент {person.Item2} " +
                                 $"(актер в {person.Item3} фильмах, " +
                                 $"член съемочной группы в {person.Item4} фильмах)");
            }
            Console.WriteLine("...");
            Console.WriteLine();


            Console.WriteLine("18. Люди, работавшие и с Martin Scorsese, и с Christopher Nolan:");
            var scorseseNolanPeople = FindPeopleWorkedWithBothDirectors(movieCredits,
                "Martin Scorsese", "Christopher Nolan");
            Console.WriteLine(string.Join(Environment.NewLine, scorseseNolanPeople));
            Console.WriteLine();


            Console.WriteLine("19. Рейтинг департаментов по среднему количеству актеров в фильмах:");
            var departmentActorCorrelation = movieCredits
                .SelectMany(movie => movie.Crew
                    .Select(crew => new { crew.Department, CastSize = movie.Cast.Count }))
                .GroupBy(x => x.Department)
                .Select(g => new
                {
                    Department = g.Key,
                    AvgCastSize = g.Average(x => x.CastSize)
                })
                .OrderByDescending(x => x.AvgCastSize);

            foreach (var dept in departmentActorCorrelation)
            {
                Console.WriteLine($"{dept.Department}: в среднем {dept.AvgCastSize:F1} актеров");
            }
            Console.WriteLine();


            Console.WriteLine("20. Анализ архетипов персонажей Johnny Depp:");
            var johnnyDeppArchetypes = movieCredits
                .SelectMany(movie => movie.Cast)
                .Where(cast => cast.Name == "Johnny Depp")
                .Select(cast => new
                {
                    Character = cast.Character,
                    FirstWord = GetFirstWord(cast.Character)
                })
                .Where(x => !string.IsNullOrEmpty(x.FirstWord))
                .GroupBy(x => x.FirstWord)
                .Select(g => new
                {
                    Archetype = g.Key,
                    Count = g.Count(),
                    Examples = g.Select(x => x.Character).Take(3).ToList()
                })
                .OrderByDescending(x => x.Count);

            foreach (var archetype in johnnyDeppArchetypes)
            {
                Console.WriteLine($"{archetype.Archetype}: {archetype.Count} раз " +
                                 $"(например: {string.Join(", ", archetype.Examples)})");
            }
        }

        private static string GetMovieTitle(IReadOnlyList<MovieCredit> movies, CastMember castMember)
        {
            return movies.FirstOrDefault(m => m.Cast.Any(c => c.Id == castMember.Id))?.Title ?? "Неизвестно";
        }

        private static List<string> FindKevinBaconSeparations(IReadOnlyList<MovieCredit> movies, int degrees)
        {
            var kevinBaconId = movies
                .SelectMany(m => m.Cast)
                .FirstOrDefault(c => c.Name == "Kevin Bacon")?.Id;

            if (kevinBaconId == null) return new List<string>();


            var degree1 = movies
                .Where(m => m.Cast.Any(c => c.Id == kevinBaconId))
                .SelectMany(m => m.Cast)
                .Where(c => c.Id != kevinBaconId)
                .Select(c => c.Name)
                .Distinct()
                .ToList();

            if (degrees == 1) return degree1;


            var degree2 = movies
                .Where(m => m.Cast.Any(c => degree1.Contains(c.Name)))
                .SelectMany(m => m.Cast)
                .Where(c => !degree1.Contains(c.Name) && c.Name != "Kevin Bacon")
                .Select(c => c.Name)
                .Distinct()
                .ToList();

            return degree2;
        }


        private static List<(string Name, string MainDepartment, int MovieCount, int CrewCount)>
            FindActorCrewPeople(IReadOnlyList<MovieCredit> movies)
        {

            var actorIds = movies
                .SelectMany(m => m.Cast)
                .Select(c => new { c.Id, c.Name })
                .Distinct()
                .ToList();

            var crewIds = movies
                .SelectMany(m => m.Crew)
                .Select(c => new { c.Id, c.Name })
                .Distinct()
                .ToList();


            var intersection = actorIds
                .Join(crewIds,
                    actor => actor.Id,
                    crew => crew.Id,
                    (actor, crew) => new { actor.Id, actor.Name })
                .Distinct()
                .ToList();

            var result = new List<(string Name, string MainDepartment, int MovieCount, int CrewCount)>();

            foreach (var person in intersection)
            {
                var crewWork = movies
                    .SelectMany(m => m.Crew)
                    .Where(c => c.Id == person.Id)
                    .GroupBy(c => c.Department)
                    .Select(g => new { Department = g.Key, Count = g.Count() })
                    .OrderByDescending(x => x.Count)
                    .FirstOrDefault();

                var movieCount = movies.Count(m => m.Cast.Any(c => c.Id == person.Id));
                var crewCount = movies.Count(m => m.Crew.Any(c => c.Id == person.Id));

                result.Add((person.Name, crewWork?.Department ?? "Неизвестно", movieCount, crewCount));
            }

            return result.OrderByDescending(x => x.MovieCount + x.CrewCount).ToList();
        }

        private static List<string> FindPeopleWorkedWithBothDirectors(
            IReadOnlyList<MovieCredit> movies, string director1, string director2)
        {
            var director1Movies = movies
                .Where(m => m.Crew.Any(c => c.Name == director1 && c.Job == "Director"))
                .SelectMany(m => m.Cast.Select(c => c.Name).Concat(m.Crew.Select(c => c.Name)))
                .Distinct()
                .ToHashSet();

            var director2Movies = movies
                .Where(m => m.Crew.Any(c => c.Name == director2 && c.Job == "Director"))
                .SelectMany(m => m.Cast.Select(c => c.Name).Concat(m.Crew.Select(c => c.Name)))
                .Distinct()
                .ToHashSet();

            return director1Movies.Intersect(director2Movies).ToList();
        }

        private static string GetFirstWord(string text)
        {
            if (string.IsNullOrWhiteSpace(text)) return "";

            var words = text.Split(' ', StringSplitOptions.RemoveEmptyEntries);
            return words.Length > 0 ? words[0] : "";
        }
    }
}