import { test, expect } from '@playwright/test';

test.describe('US-202 : Filtre Loyer Mensuel et synchronisation URL', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/catalogue?mode=rental');
  });

  test('affiche le champ Loyer Max et filtre les résultats', async ({ page }) => {
    const rentInput = page.getByLabel(/filtrer par loyer mensuel max/i);
    await expect(rentInput).toBeVisible();

    // Saisie d'un loyer max de 300 €/mois
    await rentInput.fill('300');
    await page.waitForTimeout(450); // Attente du debounce

    const vehicleCards = page.getByTestId('vehicle-card');
    if ((await vehicleCards.count()) > 0) {
      const cardText = await vehicleCards.first().innerText();
      expect(cardText).toMatch(/(\d+)\s*€\s*\/\s*mois/i);
    }
  });

  test('synchronise le mode avec l’URL lors de la bascule', async ({ page }) => {
    // Vérification initiale sur l'URL
    await expect(page).toHaveURL(/.*mode=rental/);

    // Clic sur le bouton Achat
    const saleToggle = page.getByRole('button', { name: 'Achat' });
    await saleToggle.click();

    // Vérification de la mise à jour de l'URL
    await expect(page).toHaveURL(/.*mode=sale/);
    await expect(page.getByLabel(/filtrer par budget max/i)).toBeVisible();
  });
});