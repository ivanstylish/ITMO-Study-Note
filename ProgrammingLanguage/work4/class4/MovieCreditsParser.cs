using CsvHelper;
using System;
using System.Collections.Generic;
using System.Collections.Immutable;
using System.Globalization;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace class4
{
    public class MovieCreditsParser
    {
        private readonly string _filePath;

        public MovieCreditsParser(string filePath)
        {
            _filePath = filePath;
        }

      
        public IReadOnlyList<MovieCredit> Parse()
        {
            using (var reader = new StreamReader(_filePath, Encoding.UTF8))
            using (var csv = new CsvReader(reader, CultureInfo.InvariantCulture))
            {
                csv.Context.RegisterClassMap<MovieCreditMap>();

                
                var records = csv.GetRecords<MovieCredit>().ToImmutableList();
                return records;
            }
        }
    }
}