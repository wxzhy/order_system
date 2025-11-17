import { alova } from '../request';

export function fetchPersonalStats() {
  return alova.Get<Api.Stats.PersonalResponse>('/stats/personal');
}

export function fetchSiteStats() {
  return alova.Get<Api.Stats.SiteResponse>('/stats/site');
}
