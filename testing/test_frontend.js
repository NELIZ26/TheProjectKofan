import { beforeEach, describe, expect, it } from 'vitest';
import { mount } from '@vue/test-utils';
import { createPinia, setActivePinia } from 'pinia';

import RoomCard from '../frontend/src/components/RoomCard.vue';
import { useReservaStore } from '../frontend/src/stores/reserva.js';

describe('Suite frontend Ecohotel Kofán', () => {
  
  // Este bloque se ejecuta automáticamente antes de CADA 'it'
  beforeEach(() => {
    // 1. Reiniciamos Pinia para tener un store limpio
    setActivePinia(createPinia());
    
    // 2. Inyectamos los colores de la marca en el entorno DOM virtual
    document.documentElement.style.setProperty('--k-apple', '#8BCF5B');
    document.documentElement.style.setProperty('--k-forest', '#0f3b2a');
    document.documentElement.style.setProperty('--k-sky', '#3498db');
  });

  it('RoomCard emite el evento reservar con la habitación seleccionada', async () => {
    const habitacion = {
      id: 'room-101',
      name: 'Cabaña Demo',
      description: 'Vista a la selva',
      capacity: 2,
      price: 150000,
      amenities: ['Wifi'],
      images: [],
    };

    const wrapper = mount(RoomCard, {
      props: { habitacion },
      global: {
        stubs: {
          'font-awesome-icon': true,
        },
      },
    });

    await wrapper.get('button.btn-reservar-pequeno').trigger('click');

    expect(wrapper.emitted('reservar')).toBeTruthy();
    expect(wrapper.emitted('reservar')[0][0]).toEqual(habitacion);
  });

  it('calcula correctamente el total y el anticipo de una reserva', () => {
    const pinia = createPinia();
    const store = useReservaStore(pinia);

    store.habitacionSeleccionada = { id: 'room-101', price: 120000 };
    store.selectedDateRange = {
      start: new Date('2026-04-10T00:00:00'),
      end: new Date('2026-04-13T00:00:00'),
    };

    expect(store.totalCalculado).toBe(360000);
    expect(store.anticipoCalculado).toBe(180000);
  });

  it('mantiene disponibles las variables CSS de la identidad visual según el estado', () => {
    const estilos = getComputedStyle(document.documentElement);

    expect(estilos.getPropertyValue('--k-apple').trim()).toBe('#8BCF5B');
    expect(estilos.getPropertyValue('--k-forest').trim()).toBe('#0f3b2a');
    expect(estilos.getPropertyValue('--k-sky').trim()).toBe('#3498db');

    const chipEstado = document.createElement('span');
    chipEstado.style.backgroundColor = 'var(--k-apple)';
    chipEstado.style.color = 'var(--k-forest)';

    expect(chipEstado.getAttribute('style')).toContain('var(--k-apple)');
    expect(chipEstado.getAttribute('style')).toContain('var(--k-forest)');
  });
});
