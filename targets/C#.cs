using System;

namespace MCCPU
{
    public class Program
    {
        private const MEMORY_SIZE = %memory_size;
        private const STACK_SIZE = %stack_size;
        private const REGISTER_COUNT = %register_count;

        public static void Main (string[] args)
        {
            Span<byte> stack = stackalloc byte[STACK_SIZE];
            Span<byte> registers = stackalloc byte[REGISTER_COUNT];
            byte[] memory = new byte[MEMORY_SIZE];
            %code
        }
    }
}