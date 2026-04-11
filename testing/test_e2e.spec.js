import { expect, test } from '@playwright/test';

const mockRoom = {
  id: 'room-e2e-101',
  room_number: '101',
  name: 'Cabaña Demo Kofán',
  description: 'Espacio de prueba para el flujo E2E',
  capacity: 2,
  price: 150000,
  active: true,
  is_available: true,
  type: 'cabins',
  amenities: ['Wifi', 'Baño Privado'],
  images: [],
};

test('flujo público: usuario entra, ve catálogo, reserva y recibe confirmación', async ({ page }) => {
  await page.route('**/api/rooms/', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ data: [mockRoom] }),
    });
  });

  await page.route('**/api/rooms/*/booked-dates', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([]),
    });
  });

  await page.route('**/api/reservas/invitado', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        message: '¡Reserva y comprobante recibidos con éxito!',
        reserva_id: 'res-e2e-001',
      }),
    });
  });

  await page.goto('/hospedaje/rooms');

  await expect(page.getByRole('heading', { name: /Nuestros Alojamientos/i })).toBeVisible();
  await expect(page.getByText('Cabaña Demo Kofán')).toBeVisible();

  await page.getByRole('button', { name: /Reservar/i }).first().click();

  const diasDisponibles = page.locator('.vc-day-content:not(.is-disabled)');
  await diasDisponibles.nth(10).click();
  await diasDisponibles.nth(12).click();

  await page.locator('input[placeholder="Ej: Juan Pérez"]').fill('Nelson Prueba');
  await page.locator('input[placeholder="310 123 4567"]').fill('3201234567');
  await page.locator('input[placeholder="ejemplo@correo.com"]').fill('nelson@example.com');

  await page.locator('input[type="file"]').setInputFiles({
    name: 'comprobante.png',
    mimeType: 'image/png',
    buffer: Buffer.from('fake-image-content'),
  });

  await page.getByRole('button', { name: /Confirmar y Enviar/i }).click();

  await expect(page.getByText(/Reserva Solicitada|recibido tu comprobante/i)).toBeVisible();
});
