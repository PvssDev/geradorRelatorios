/**
 * Ordenação natural (humana) idêntica a chave_ordenacao_natural do Python.
 * Garante que 'Foto 2.jpg' venha antes de 'Foto 10.jpg', ignorando variações de acento e caixa.
 */
const collator = new Intl.Collator("pt-BR", {
  numeric: true,
  sensitivity: "base",
});

export function compararNomesNatural(a: string, b: string): number {
  return collator.compare(a, b);
}

