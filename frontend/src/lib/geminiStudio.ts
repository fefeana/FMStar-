import { GoogleGenAI } from '@google/genai';

// استدعاء المفتاح المخزن في أسرار النظام بأمان
const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });

export async function generateStudioContent(promptText: string) {
  try {
    const response = await ai.models.generateContent({
      model: 'gemini-2.5-flash',
      contents: promptText,
    });
    return response.text;
  } catch (error) {
    console.error("خطأ في الاتصال بنموذج جيمي:", error);
    return null;
  }
}
