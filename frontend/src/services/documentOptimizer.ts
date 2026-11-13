import JSZip from "jszip";
import { comprimirFotoParaEnvio } from "./imageCompressor";

const MEDIA_ENTRY_RE = /^(word|xl)\/media\/.+\.(jpe?g|png|webp)$/i;

/**
 * Otimiza arquivos Office baseados em ZIP (.docx e .xlsx) no navegador antes do envio.
 * Comprime imagens embutidas em word/media ou xl/media e recompacta os XMLs com DEFLATE,
 * reduzindo arquivos grandes para caber com folga no limite de 4.5 MB da Vercel.
 */
export async function otimizarArquivoOfficeParaEnvio(
  file: File,
  options?: {
    thresholdBytes?: number;
    maxWidth?: number;
    maxHeight?: number;
    quality?: number;
  }
): Promise<File> {
  const thresholdBytes = options?.thresholdBytes ?? 900 * 1024;
  const maxWidth = options?.maxWidth ?? 960;
  const maxHeight = options?.maxHeight ?? 720;
  const quality = options?.quality ?? 0.72;

  const lowerName = file.name.toLowerCase();
  if (
    file.size <= thresholdBytes ||
    (!lowerName.endsWith(".docx") && !lowerName.endsWith(".xlsx"))
  ) {
    return file;
  }

  try {
    const zip = await JSZip.loadAsync(file);
    const mediaPaths = Object.keys(zip.files).filter(
      (path) => !zip.files[path].dir && MEDIA_ENTRY_RE.test(path)
    );

    for (const mediaPath of mediaPaths) {
      const entry = zip.files[mediaPath];
      const rawBytes = await entry.async("uint8array");
      if (rawBytes.byteLength <= 90 * 1024) continue;

      const ext = mediaPath.split(".").pop()?.toLowerCase() || "jpg";
      const mime = ext === "png" ? "image/png" : ext === "webp" ? "image/webp" : "image/jpeg";
      const tempFile = new File([rawBytes], mediaPath.split("/").pop() || "media.jpg", {
        type: mime,
      });

      const compressed = await comprimirFotoParaEnvio(
        tempFile,
        maxWidth,
        maxHeight,
        quality
      );

      if (compressed.size < rawBytes.byteLength) {
        const compressedBuffer = await compressed.arrayBuffer();
        zip.file(mediaPath, compressedBuffer);
      }
    }

    const optimizedBlob = await zip.generateAsync({
      type: "blob",
      compression: "DEFLATE",
      compressionOptions: { level: 6 },
    });

    if (optimizedBlob.size >= file.size) {
      return file;
    }

    return new File([optimizedBlob], file.name, {
      type: file.type,
      lastModified: file.lastModified,
    });
  } catch {
    return file;
  }
}

