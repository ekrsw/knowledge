import React, { useState, useMemo } from 'react';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { LoginForm } from './components/Auth/LoginForm';
import { Header } from './components/Layout/Header';
import { SearchFiltersComponent } from './components/FAQ/SearchFilters';
import { FAQList } from './components/FAQ/FAQList';
import { FAQDetail } from './components/FAQ/FAQDetail';
import { FAQForm } from './components/FAQ/FAQForm';
import { PostTypeSelection } from './components/FAQ/PostTypeSelection';
import { DeleteProposalForm } from './components/FAQ/DeleteProposalForm';
import { ApprovalQueue } from './components/Approval/ApprovalQueue';
import { ApprovalForm } from './components/Approval/ApprovalForm';
import { MyPostsList } from './components/MyPosts/MyPostsList';
import { FAQ, SearchFilters } from './types';
import { mockFAQs } from './data/mockData';

function AppContent() {
  const { user } = useAuth();
  const [currentPage, setCurrentPage] = useState('search');
  const [selectedFAQ, setSelectedFAQ] = useState<FAQ | null>(null);
  const [editingFAQ, setEditingFAQ] = useState<FAQ | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  const [showPostTypeSelection, setShowPostTypeSelection] = useState(false);
  const [showDeleteProposal, setShowDeleteProposal] = useState(false);
  const [faqs, setFaqs] = useState<FAQ[]>(mockFAQs);
  const [searchFilters, setSearchFilters] = useState<SearchFilters>({
    keyword: '',
    articleNumber: '',
    importantOnly: false,
    category: '',
    approvalGroup: '',
    sortBy: 'articleNumber',
    sortOrder: 'asc',
  });

  const filteredFAQs = useMemo(() => {
    let filtered = faqs.filter(faq => faq.status === 'approved');

    if (searchFilters.keyword) {
      const keyword = searchFilters.keyword.toLowerCase();
      filtered = filtered.filter(faq =>
        faq.title.toLowerCase().includes(keyword) ||
        faq.question.toLowerCase().includes(keyword) ||
        faq.answer.toLowerCase().includes(keyword) ||
        faq.keywords.some(k => k.toLowerCase().includes(keyword))
      );
    }

    if (searchFilters.articleNumber) {
      filtered = filtered.filter(faq =>
        faq.articleNumber.includes(searchFilters.articleNumber)
      );
    }

    if (searchFilters.importantOnly) {
      filtered = filtered.filter(faq => faq.isImportant);
    }

    if (searchFilters.category) {
      filtered = filtered.filter(faq => faq.category === searchFilters.category);
    }

    if (searchFilters.approvalGroup) {
      filtered = filtered.filter(faq => faq.approvalGroup === searchFilters.approvalGroup);
    }

    // Sort
    filtered.sort((a, b) => {
      let aValue: string | Date;
      let bValue: string | Date;

      switch (searchFilters.sortBy) {
        case 'articleNumber':
          aValue = a.articleNumber;
          bValue = b.articleNumber;
          break;
        case 'createdAt':
          aValue = new Date(a.createdAt);
          bValue = new Date(b.createdAt);
          break;
        case 'approvedAt':
          aValue = new Date(a.approvedAt || 0);
          bValue = new Date(b.approvedAt || 0);
          break;
        default:
          return 0;
      }

      if (aValue < bValue) return searchFilters.sortOrder === 'asc' ? -1 : 1;
      if (aValue > bValue) return searchFilters.sortOrder === 'asc' ? 1 : -1;
      return 0;
    });

    return filtered;
  }, [faqs, searchFilters]);

  const pendingFAQs = useMemo(() => {
    return faqs.filter(faq => faq.status === 'pending');
  }, [faqs]);

  const myPosts = useMemo(() => {
    return faqs.filter(faq => faq.author === user?.id);
  }, [faqs, user?.id]);

  const handleSearch = () => {
    // Search is handled by the useMemo above
  };

  const handleFAQSave = (faqData: Partial<FAQ>) => {
    if (editingFAQ) {
      setFaqs(prev => prev.map(faq => 
        faq.id === editingFAQ.id 
          ? { ...faq, ...faqData }
          : faq
      ));
      setEditingFAQ(null);
    } else {
      const newFAQ: FAQ = {
        id: Date.now().toString(),
        articleNumber: faqData.articleNumber || `KBA-${Date.now().toString().slice(-5)}-${Math.floor(Math.random() * 100000)}`,
        title: faqData.title || '',
        category: faqData.category || '',
        approvalGroup: faqData.approvalGroup || '',
        keywords: faqData.keywords || [],
        isImportant: faqData.isImportant || false,
        publicStartDate: faqData.publicStartDate || '',
        publicEndDate: faqData.publicEndDate || '',
        question: faqData.question || '',
        answer: faqData.answer || '',
        additionalComment: faqData.additionalComment,
        notes: faqData.notes,
        status: faqData.status || 'pending',
        author: user?.id || '',
        authorName: user?.name || '',
        createdAt: new Date().toISOString(),
      };
      setFaqs(prev => [...prev, newFAQ]);
      setIsCreating(false);
    }
  };

  const handleDeleteProposal = (articleNumber: string, reason: string) => {
    const deleteProposal: FAQ = {
      id: Date.now().toString(),
      articleNumber: `DEL-${Date.now().toString().slice(-5)}-${Math.floor(Math.random() * 100000)}`,
      title: `削除提案: ${articleNumber}`,
      category: '削除提案',
      approvalGroup: '',
      keywords: ['削除提案'],
      isImportant: false,
      publicStartDate: new Date().toISOString().split('T')[0],
      publicEndDate: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      question: `記事番号 ${articleNumber} の削除を提案します。`,
      answer: `削除理由: ${reason}`,
      additionalComment: `対象記事: ${articleNumber}`,
      notes: '',
      status: 'pending',
      author: user?.id || '',
      authorName: user?.name || '',
      createdAt: new Date().toISOString(),
    };
    setFaqs(prev => [...prev, deleteProposal]);
    setShowDeleteProposal(false);
    setCurrentPage('search');
  };

  const handleApprove = (faq: FAQ, comment: string, approvalGroup: string) => {
    setFaqs(prev => prev.map(f => 
      f.id === faq.id 
        ? { 
            ...f, 
            status: 'approved', 
            approvedAt: new Date().toISOString(),
            approvedBy: user?.id,
            approvalComment: comment,
            approvalGroup
          }
        : f
    ));
    setSelectedFAQ(null);
  };

  const handleReject = (faq: FAQ, reason: string) => {
    setFaqs(prev => prev.map(f => 
      f.id === faq.id 
        ? { 
            ...f, 
            status: 'rejected', 
            rejectedAt: new Date().toISOString(),
            rejectionReason: reason
          }
        : f
    ));
    setSelectedFAQ(null);
  };

  const handleDelete = (faq: FAQ) => {
    setFaqs(prev => prev.filter(f => f.id !== faq.id));
  };

  const renderPageContent = () => {
    if (showPostTypeSelection) {
      return (
        <PostTypeSelection
          onSelectModification={() => {
            setShowPostTypeSelection(false);
            setIsCreating(true);
          }}
          onSelectDeletion={() => {
            setShowPostTypeSelection(false);
            setShowDeleteProposal(true);
          }}
          onBack={() => {
            setShowPostTypeSelection(false);
            setCurrentPage('search');
          }}
        />
      );
    }

    if (showDeleteProposal) {
      return (
        <DeleteProposalForm
          onSubmit={handleDeleteProposal}
          onCancel={() => {
            setShowDeleteProposal(false);
            setShowPostTypeSelection(true);
          }}
        />
      );
    }

    if (selectedFAQ && currentPage === 'pending') {
      return (
        <ApprovalForm
          faq={selectedFAQ}
          onApprove={handleApprove}
          onReject={handleReject}
          onEdit={(faq) => {
            setEditingFAQ(faq);
            setSelectedFAQ(null);
            setCurrentPage('create');
          }}
          onBack={() => setSelectedFAQ(null)}
        />
      );
    }

    if (selectedFAQ) {
      return (
        <FAQDetail
          faq={selectedFAQ}
          onBack={() => setSelectedFAQ(null)}
          onEdit={(faq) => {
            setEditingFAQ(faq);
            setSelectedFAQ(null);
            setCurrentPage('create');
          }}
          onDelete={handleDelete}
          canEdit={user?.id === selectedFAQ.author}
        />
      );
    }

    if (isCreating || editingFAQ) {
      return (
        <FAQForm
          faq={editingFAQ || undefined}
          onSave={handleFAQSave}
          onCancel={() => {
            setIsCreating(false);
            setEditingFAQ(null);
          }}
          isEditing={!!editingFAQ}
        />
      );
    }

    switch (currentPage) {
      case 'search':
        return (
          <div className="space-y-6">
            <SearchFiltersComponent
              filters={searchFilters}
              onFiltersChange={setSearchFilters}
              onSearch={handleSearch}
            />
            <FAQList
              faqs={filteredFAQs}
              onFAQClick={setSelectedFAQ}
            />
          </div>
        );

      case 'create':
        return (
          <FAQForm
            onSave={handleFAQSave}
            onCancel={() => setCurrentPage('search')}
          />
        );

      case 'pending':
        if (user?.role !== 'sv' && user?.role !== 'admin') {
          return <div className="text-center py-12">アクセス権限がありません</div>;
        }
        return (
          <ApprovalQueue
            pendingFAQs={pendingFAQs}
            onApprove={handleApprove}
            onReject={handleReject}
            onEdit={(faq) => {
              setEditingFAQ(faq);
              setCurrentPage('create');
            }}
            onView={setSelectedFAQ}
          />
        );

      case 'myposts':
        return (
          <MyPostsList
            posts={myPosts}
            onEdit={(faq) => {
              setEditingFAQ(faq);
              setCurrentPage('create');
            }}
            onDelete={handleDelete}
            onView={setSelectedFAQ}
            onResubmit={(faq) => {
              setEditingFAQ(faq);
              setCurrentPage('create');
            }}
          />
        );

      case 'admin':
        if (user?.role !== 'admin') {
          return <div className="text-center py-12">アクセス権限がありません</div>;
        }
        return (
          <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">管理機能</h2>
            <p className="text-gray-600">管理機能は開発中です。</p>
          </div>
        );

      default:
        return null;
    }
  };

  const handlePageChange = (page: string) => {
    if (page === 'create') {
      setShowPostTypeSelection(true);
    } else if (page === 'myposts') {
      setCurrentPage('myposts');
    } else {
      setCurrentPage(page);
      setSelectedFAQ(null);
      setIsCreating(false);
      setEditingFAQ(null);
      setShowPostTypeSelection(false);
      setShowDeleteProposal(false);
    }
  };

  if (!user) {
    return <LoginForm />;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header 
        currentPage={currentPage} 
        onPageChange={handlePageChange}
      />
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {renderPageContent()}
      </main>
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;