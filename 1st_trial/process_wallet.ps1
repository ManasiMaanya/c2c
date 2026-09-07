Add-Type -AssemblyName System.Drawing

$code = @"
using System;
using System.Drawing;
using System.Drawing.Imaging;
using System.Runtime.InteropServices;

public class WalletProcessor {
    public static void ProcessImage(string inputPath, string outputPath) {
        using (Bitmap src = new Bitmap(inputPath)) {
            int width = src.Width;
            int height = src.Height;
            Bitmap dst = new Bitmap(width, height, PixelFormat.Format32bppArgb);

            BitmapData srcData = src.LockBits(new Rectangle(0, 0, width, height), ImageLockMode.ReadOnly, PixelFormat.Format32bppArgb);
            BitmapData dstData = dst.LockBits(new Rectangle(0, 0, width, height), ImageLockMode.WriteOnly, PixelFormat.Format32bppArgb);

            int bytes = Math.Abs(srcData.Stride) * height;
            byte[] rgbValues = new byte[bytes];
            byte[] resultValues = new byte[bytes];

            Marshal.Copy(srcData.Scan0, rgbValues, 0, bytes);

            for (int i = 0; i < bytes; i += 4) {
                byte b = rgbValues[i];
                byte g = rgbValues[i + 1];
                byte r = rgbValues[i + 2];
                byte a = rgbValues[i + 3];

                // Check background pixels
                double minVal = Math.Min(r, Math.Min(g, b));
                double maxVal = Math.Max(r, Math.Max(g, b));
                double colorDiff = maxVal - minVal;

                if (r >= 248 && g >= 248 && b >= 248) {
                    // Pure white background -> fully transparent
                    resultValues[i] = 0;
                    resultValues[i + 1] = 0;
                    resultValues[i + 2] = 0;
                    resultValues[i + 3] = 0;
                } else if (minVal > 195 && colorDiff < 30) {
                    // Near-white outer edge halo -> smooth alpha transition + unblend white
                    double alphaFrac = 1.0 - (minVal - 195.0) / 53.0;
                    alphaFrac = Math.Max(0.0, Math.Min(1.0, alphaFrac));
                    
                    byte finalA = (byte)(alphaFrac * 255.0);
                    
                    byte finalR = (byte)Math.Max(0, Math.Min(255, (r - 255 * (1 - alphaFrac)) / Math.Max(0.01, alphaFrac)));
                    byte finalG = (byte)Math.Max(0, Math.Min(255, (g - 255 * (1 - alphaFrac)) / Math.Max(0.01, alphaFrac)));
                    byte finalB = (byte)Math.Max(0, Math.Min(255, (b - 255 * (1 - alphaFrac)) / Math.Max(0.01, alphaFrac)));

                    resultValues[i] = finalB;
                    resultValues[i + 1] = finalG;
                    resultValues[i + 2] = finalR;
                    resultValues[i + 3] = finalA;
                } else {
                    // Wallet / blue glow / coin pixels -> keep 100% opaque
                    resultValues[i] = b;
                    resultValues[i + 1] = g;
                    resultValues[i + 2] = r;
                    resultValues[i + 3] = 255;
                }
            }

            Marshal.Copy(resultValues, 0, dstData.Scan0, bytes);
            src.UnlockBits(srcData);
            dst.UnlockBits(dstData);

            dst.Save(outputPath, ImageFormat.Png);
        }
    }
}
"@

Add-Type -TypeDefinition $code -ReferencedAssemblies "System.Drawing.dll"

$inputPath = Resolve-Path "wallet.png"
$outputPath = Join-Path (Get-Location) "wallet_transparent.png"
[WalletProcessor]::ProcessImage($inputPath, $outputPath)
Write-Host "Processed wallet artwork saved to: $outputPath"
