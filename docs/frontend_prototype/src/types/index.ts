export interface User {
  id: string;
  name: string;
  email: string;
  role: 'operator' | 'sv' | 'admin';
  group: string;
  avatar?: string;
}

export interface FAQ {
  id: string;
  articleNumber: string;
  title: string;
  category: string;
  approvalGroup: string;
  keywords: string[];
  isImportant: boolean;
  publicStartDate: string;
  publicEndDate: string;
  question: string;
  answer: string;
  additionalComment?: string;
  notes?: string;
  status: 'draft' | 'pending' | 'approved' | 'rejected';
  author: string;
  authorName: string;
  createdAt: string;
  approvedAt?: string;
  approvedBy?: string;
  rejectedAt?: string;
  rejectionReason?: string;
  approvalComment?: string;
}

export interface Category {
  id: string;
  name: string;
  color: string;
}

export interface ApprovalGroup {
  id: string;
  name: string;
  description: string;
}

export interface SearchFilters {
  keyword: string;
  articleNumber: string;
  importantOnly: boolean;
  category: string;
  approvalGroup: string;
  sortBy: 'articleNumber' | 'createdAt' | 'approvedAt';
  sortOrder: 'asc' | 'desc';
}

export interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
}