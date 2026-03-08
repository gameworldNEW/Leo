namespace LeoPlugins {
    public class Utils {
        public static double MyPower(double baseNum, double exp) {
            return System.Math.Pow(baseNum, exp);
        }
        public static string SayHello(string name) {
            return "Привет из C#, " + name + "!";
        }
    }
}
