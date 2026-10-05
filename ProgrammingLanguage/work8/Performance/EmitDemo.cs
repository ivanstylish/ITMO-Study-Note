using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection.Emit;
using System.Text;
using System.Threading.Tasks;

namespace class8.Performance
{

    public delegate double FastCalc(double a, double b, double c);

    public static class EmitDemo
    {
        public static FastCalc CreateDynamicMethod()
        {
            var dm = new DynamicMethod("Calc", typeof(double), new[] { typeof(double), typeof(double), typeof(double) });
            var il = dm.GetILGenerator();

            il.Emit(OpCodes.Ldarg_0);  // a
            il.Emit(OpCodes.Ldarg_1);  // b
            il.Emit(OpCodes.Add);      // a + b
            il.Emit(OpCodes.Ldarg_2);  // c
            il.Emit(OpCodes.Mul);      // (a + b) * c
            il.Emit(OpCodes.Ret);

            return (FastCalc)dm.CreateDelegate(typeof(FastCalc));
        }
    }
}
