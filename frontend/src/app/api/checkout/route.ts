import { NextResponse } from 'next/server';

export async function POST(req: Request) {
  try {
    const { planId, userId } = await req.json();

    // محاكاة إنشاء جلسة دفع عبر Stripe أو بوابة الدفع المعتمدة
    const checkoutSession = {
      id: `cs_test_${Math.random().toString(36).substring(7)}`,
      url: `https://checkout.stripe.com/pay/fmstar_${planId}?user=${userId}`,
      status: 'open',
    };

    return NextResponse.json({ success: true, session: checkoutSession });
  } catch (error) {
    return NextResponse.json({ error: 'فشل في إنشاء عملية الدفع' }, { status: 500 });
  }
}
